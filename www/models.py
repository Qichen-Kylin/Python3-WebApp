#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Models for user, blog, comment.
'''

__author__ = 'Kylin'

import time, uuid

from orm import Model, StringField, BooleanField, FloatField, TextField

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

#测试
if __name__== '__main__':
    
    async def test():
        await create_pool(loop,user='webapp', password='123456', database='webapp')
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