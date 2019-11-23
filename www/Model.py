#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Kylin'

import logging
import asyncio 
import aiomysql

import time, uuid

def log(sql, args=()):
    logging.info('SQL: %s' % sql)

'''创建连接池
- 需要创建一个全局的连接池，每个HTTP请求都可以从连接池中直接获取数据库连接。
- 使用连接池的好处是不必频繁地打开和关闭数据库连接，而是能复用就尽量复用。
- 连接池由全局变量`__pool`存储，缺省情况下将编码设置为`utf8`，自动提交事务。
'''
async def create_pool(loop, **kw):
    logging.info('create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('host', '10.80.36.17'), #host参数localhost
        port=kw.get('port', 3306),        #port参数是3306，标准默认port
        user=kw['user'],
        password=kw['password'],
        db=kw['database'],
        charset=kw.get('charset', 'utf8'), #charset参数是utf8
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop  #事件循环处理
    )

'''封装SELECT操作
- 封装`SELECT`操作为`select()`函数执行，需要传入SQL语句及SQL参数：
- SQL语句占位符是`？`，而MySQL占位符是`%s`,`select()`函数内部自动替换。*注意要始终坚持使用带参数的SQL，而不是自己拼接SQL字符串，这样可以防止SQL注入攻击。*
- `cur.execute('select * from user where id = %s', ('1',))`
- 如果传入size参数，就通过`fetchmany`获得最多指定数量的记录，否则就通过`fetchall`获得所有记录。
'''
async def select(sql, args, size=None):
    log(sql, args)
    global __pool
    async with __pool.get() as conn: #打开pool的方法,或--> with __pool.get() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur: #创建游标,aiomysql.DictCursor的作用使生成结果是一个dict
            await cur.execute(sql.replace('?', '%s'), args or ()) #执行sql语句，sql语句的占位符是'?',而Mysql的占位符是'%s'
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
        logging.info('rows returned: %s' % len(rs))
        return rs

'''封装INSERT,UPDATE,DELETE操作
- 要执行`INSERT`、`UPDATE`、`DELETE`语句，可以定义一个通用的`execute()`函数，因为这3类SQL的执行都需要相同的参数，以及返回一个整数表示影响的行数。
- `execute()`函数与`select()`函数所不同的是，cursor对象不返回结果集，而是通过`rowcount`返回结果数。
'''
async def execute(sql, args, autocommit=True):
    log(sql)
    async with __pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise
        return affected

# 用于输出元类中创建sql_insert语句中的占位符
def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)

# Field类：负责保存数据库表的字段名、字段类型、是否主键、默认值...
class Field(object):

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)

#在Field的基础上，进一步定义各种类型的Field。
class StringField(Field):

    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)

class BooleanField(Field):

    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)

class IntegerField(Field):

    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)

class FloatField(Field):

    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)

class TextField(Field):

    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)

#元类：即创建类的类，创建类的时候只需要将metaclass=元类，元类需要继承type而不是object,因为type就是元类。
#元类 `ModelMetaclass` 负责分类、整理收集的数据并以此创建一些类属性(如SQL语句)供基类作为参数。
class ModelMetaclass(type):

    def __new__(cls, name, bases, attrs):  #当前准备创建的类的对象；类的名字；类继承的父类集合；类的方法集合。
        if name=='Model':  #排除掉对Model类的修改；
            return type.__new__(cls, name, bases, attrs)  
        tableName = attrs.get('__table__', None) or name
        logging.info('found model: %s (table: %s)' % (name, tableName))
        # 获取所有的Field和主键名:
        mappings = dict()  #保存映射关系
        fields = []        #保存除主键外的属性
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info('  found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
                if v.primary_key:
                    # 找到主键:
                    if primaryKey:
                        raise StandardError('Duplicate primary key for field: %s' % k)
                    primaryKey = k    #此列设为列表的主键
                else:
                    fields.append(k)  #保存除主键外的属性
        if not primaryKey:
            raise StandardError('Primary key not found.')
        for k in mappings.keys():
            attrs.pop(k)   #从类属性中删除Field属性,否则，容易造成运行时错误（实例的属性会遮盖类的同名属性）
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))  #转换为sql语法
        #创建供Model类使用属性
        attrs['__mappings__'] = mappings        # 保存属性和列的映射关系
        attrs['__table__'] = tableName          # 表名
        attrs['__primary_key__'] = primaryKey   # 主键属性名
        attrs['__fields__'] = fields            # 除主键外的属性名
        #构造默认的SELECT、 INSERT、 UPDATE、DELETE语句:
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs)

#基类`Model`负责执行操作，比如数据库的存储、读取，查找等操作等
class Model(dict, metaclass=ModelMetaclass): #从元类创建类：指定元类 metaclass=ModelMetaclass

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):  
        return getattr(self, key, None)  #直接调回内置函数，这里没有下划符,这里None的用处,是为了当user没有赋值数据时，返回None，调用于update。

    def getValueOrDefault(self, key):
        value = getattr(self, key, None) #第三个参数None，可以在没有返回数值时，返回None，调用于save。
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s: %s' % (key, str(value)))
                setattr(self, key, value)
        return value
    #添加class方法，就可以让所有子类调用class方法：
    @classmethod
    async def findAll(cls, where=None, args=None, **kw):
        ' find objects by where clause. '
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = await select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        ' find number by select and where. '
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    @classmethod
    async def find(cls, pk):
        ' find object by primary key. '
        rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s' % rows)

    async def update(self):
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await execute(self.__update__, args)
        if rows != 1:
            logging.warn('failed to update by primary key: affected rows: %s' % rows)

    async def remove(self):
        args = [self.getValue(self.__primary_key__)] #这里不能使用list()-->'int' object is not iterable
        rows = await execute(self.__delete__, args)
        if rows != 1:
            logging.warn('failed to remove by primary key: affected rows: %s' % rows)
            
            
def next_id():  #随机创建唯一id，作为主键缺省值
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)

class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)

class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)
    
    
if __name__== '__main__':
    
    async def test():
        await create_pool(loop, user='webapp', password='123456', database='webapp')
        u = User(name='chenqi', email='chenqi@ccpd.com.cn', passwd='1234567890', image='about:blank')
        await u.save()
        a = await u.findall() #这个要打印才显示出来
        print(a)
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
    #在关闭event loop之前，首先需要关闭连接池。
    __pool.close()                               
    loop.run_until_complete(__pool.wait_closed())
    loop.close()