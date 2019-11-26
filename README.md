# Python3-WebApp
基于Python3的Web开发

## HTTP请求的生命周期
![项目流程图](https://github.com/Qichen-Kylin/Python3-WebApp/blob/develop/www/app/static/img/FlowChart.png)

1. 客户端（浏览器）发起请求  
2. 路由分发请求（这个框架自动帮处理），add_routes函数就是注册路由。  
3. 中间件预处理  
   - 打印日志
   - 验证用户登陆
   - 收集Request（请求）的数据
4. RequestHandler清理参数并调用控制器（Django和Flask把这些处理请求的控制器称为view functions）
5. 控制器做相关的逻辑判断，有必要时通过ORM框架处理Model的事务。
6. 模型层的主要事务是数据库的查增改删。
7. 控制器再次接管控制权，返回相应的数据。
8. Response_factory根据控制器传过来的数据产生不同的响应。
9. 客户端（浏览器）接收到来自服务器的响应。


# WebApp实战
##  Day-1 搭建开发环境
***2019-11-19 星期二***
1. 确认当前系统安装的Python版本：
```Markdown
(base) C:\Windows\system32>python --version
Python 3.6.5 :: Anaconda, Inc.
```

2. 安装MySQL数据库：从[MySQL官方网站](https://dev.mysql.com/downloads/mysql/5.6.html "MySQL官方网站")下载并安装。

3. 然后，用`pip`安装开发Web App需要的第三方库：
 - **异步框架 aiohttp:** `pip install aiohttp`
 - **前端模板引擎 jinja2:** `pip install jinja2`
 - **MySQL的python异步驱动程序aiomysql：** `pip install aiomysql`

4. 项目结构
选择一个工作目录，建立大致如下的目录结构：
```Markdown
python3-webapp/  <-- 根目录
|
+- backup/       <-- 备份目录
|
+- conf/         <-- 配置文件
|
+- dist/         <-- 打包目录
|
+- www/          <-- Web目录，存放.py文件
| |
| +- static/     <-- 存放静态文件
| |
| +- templates/  <-- 存放模板文件
|
+- LICENSE       <-- 代码LICENSE
```
创建好工作目录结构后，建立**Git仓库**并同步至[`GitHub`](https://github.com/Qichen-Kylin/Python3-WebApp "Qichen-Kylin/Python3-WebApp")，版本控制保证代码修改安全:
```Markdown
PD000731_陈麒@IT-13 MINGW64 /d/CCPD-G8.6/Python3-WebApp
$ git init
Initialized empty Git repository in D:/CCPD-G8.6/Python3-WebApp/.git/
PD000731_陈麒@IT-13 MINGW64 /d/CCPD-G8.6/Python3-WebApp (master)
$ git remote add origin https://github.com/Qichen-Kylin/Python3-WebApp.git
PD000731_陈麒@IT-13 MINGW64 /d/CCPD-G8.6/Python3-WebApp (master)
$ git pull origin master
PD000731_陈麒@IT-13 MINGW64 /d/CCPD-G8.6/Python3-WebApp (master)
$ git push -u origin master
PD000731_陈麒@IT-13 MINGW64 /d/CCPD-G8.6/Python3-WebApp (master)
$ mkdir -p backup conf dist www/static www/templates
PD000731_陈麒@IT-13 MINGW64 /d/CCPD-G8.6/Python3-WebApp (master)
$ touch LICENSE
PD000731_陈麒@IT-13 MINGW64 /d/CCPD-G8.6/Python3-WebApp (master)
$ ls
backup/  conf/  dist/  LICENSE  README.md  www/
```

##  Day-2 编写Web App骨架
该**WebApp**建立在`asyncio`的基础上，用`aiohttp`写一个基本骨架`app.py`:
```Markdown
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Kylin'

'''
async web application.
Python 3.5开始的新语法:
1. 把 @asyncio.coroutine 替换为 async；
2. 把 yield from 替换为 await 。
'''

import logging; logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web

def index(request):
    return web.Response(body=b'<h1>Awesome</h1>',headers={'content-type':'text/html'})

async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    # loop.create_server则利用asyncio创建TCP服务
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
```
**WebApp**将在`9000`端口监听http请求，并对首页`/`进行响应。

------------
- **协程（Coroutine）**
1. 协程，又称微线程。协程看上去也是子程序，但是执行过程中，在子程序内部可以中断，然后转而执行别的子程序，在适当的时间再返回来接着执行中断的子程序。

2. 协程的特点在于是一个线程执行，和多线程相比协程最大的优势就是极高的执行效率。因为子程序切换不是线程切换，而是程序自身控制，因此，没有线程切换的开销，和多线程比，线程数量越多，协程的性能优势就越明显；第二大优势就是不需要多线程的锁机制，因为只有一个线程，也不存在同时写变量冲突，在协程中控制共享资源不加锁，只需要判断状态就好了，所以执行效率比多线程高很多。

3. Python对协程的支持是通过`generator`实现的。在generator中，不但可以通过循环来迭代，还可以不断的调用`next()`函数获取有`yield`语句返回的下一个值。Python的yield还可以接收调用者发出的参数。

- **asyncio**
1. `asyncio`是直接内置对异步IO的支持。`asyncio`的编程模型就是一个消息循环。我们从`asyncio`模块中直接获取一个`EventLoop`的引用，然后把需要执行的`协程`扔到`EventLoop`中执行，就实现了异步IO。

2. `asyncio`提供了完善的的异步IO支持；异步操作需要在`coroutine(协同程序)`中通过`yield from`完成；多个`coroutine`可以分装成一组Task然后并发执行。

3. `asyncio`可以实现单线程并发IO操作。如果将其只用在客户端，则发挥的威力不大；如果将它放在服务器端，例如Web服务器，由于http连接就是IO操作，因此可以用`单线程+协程`实现多用户的高并发支持。

##  Day-3 编写ORM
[ORM](https://blog.csdn.net/zhmpql/article/details/82262776 "原文链接")，即`Object-Relational Mapping（对象关系映射）`，它的作用是在关系型数据库和业务实体对象之间作一个映射，这样，我们在具体的操作业务对象的时候，就不需要再去和复杂的SQL语句打交道，只需简单的操作对象的属性和方法。
**总结：简单来说ORM就是封装数据库的操作。**
> - 优点：
1. 只需要面向对象编程, 不需要面向数据库编写代码.：
对数据库的操作都转化成对类属性和方法的操作，不用编写各种数据库的sql语句。
2. 实现了数据模型与数据库的解耦，屏蔽了不同数据库操作的差异：
不在关注用的是mysql、oracle….等，通过简单的配置就可以轻松更换数据库，而不需要修改代码。
- 缺点：
1. 相比较直接使用SQL语句操作数据库,有性能损失。
2. 根据对象的操作转换成SQL语句,根据查询的结果转化成对象, 在映射过程中有性能损失。

### 设计背景与思路
- 在一个Web App中，所有的数据，包括用户信息，用户发布的日志，评论都放在数据库中。*本次实战使用MySQL作为数据库。*
- Web App中，有许多地方都要用到数据库，访问数据要创建数据库连接，创建游标对象，然后执行SQL语句，最后要处理异常，清理资源等。这些访问数据库的的代码如果分散到各个函数之中，势必无法维护，也不利于代码复用。
- 所以，首先要把常用的`SELECT,INSERT,UPDATE,DELETE`操作用函数分装起来。
- 由于Web框架使用了基于`asyncio`的`aiohttp`，这是基于协程的异步模型（*异步编程的原则：一旦决定使用异步，则系统每一层都必须是异步*）。Web App框架采用异步IO编程，而`aiomysql`为MySQL数据库提供了异步IO的驱动。

### 创建连接池
- 需要创建一个全局的连接池，每个HTTP请求都可以从连接池中直接获取数据库连接。
- 使用连接池的好处是不必频繁地打开和关闭数据库连接，而是能复用就尽量复用。
- 连接池由全局变量`__pool`存储，缺省情况下将编码设置为`utf8`，自动提交事务。

### 封装SELECT操作
- 封装`SELECT`操作为`select()`函数执行，需要传入SQL语句及SQL参数：
- SQL语句占位符是`？`，而MySQL占位符是`%s`,`select()`函数内部自动替换。*注意要始终坚持使用带参数的SQL，而不是自己拼接SQL字符串，这样可以防止SQL注入攻击。*
- `cur.execute(&#39;select * from user where id = %s&#39;, (&#39;1&#39;,))`
- 如果传入size参数，就通过`fetchmany`获得最多指定数量的记录，否则就通过`fetchall`获得所有记录。

### 封装INSERT,UPDATE,DELETE操作
- 要执行`INSERT`、`UPDATE`、`DELETE`语句，可以定义一个通用的`execute()`函数，因为这3类SQL的执行都需要相同的参数，以及返回一个整数表示影响的行数。
- `execute()`函数与`select()`函数所不同的是，cursor对象不返回结果集，而是通过`rowcount`返回结果数。

### 创建Field类
- `Field类`：负责保存数据库表的字段名、字段类型、是否主键、默认值...
- 在Field的基础上，进一步定义各种类型的Field：`StringField`、`IntegerField`等。

### 创建元类ModelMetaclass
- 元类：即创建类的类，创建类的时候只需要指定`metaclass=元类`，元类需要继承`type`而不是`object`,因为type就是元类。
- 元类 `ModelMetaclass` 负责分类、整理收集的数据并以此创建一些类属性(如SQL语句)供基类作为参数。

### 创建基类Model
- 基类`Model`负责执行操作，比如数据库的存储、读取，查找等操作等。
- 基类中方法都基于`asyncio`的装饰，所以方法都是协程。
- 任何继承自`Model`的类，会自动通过`ModelMetaclass`扫描映射关系，并存储到自身的类属性中。

# WebApp实战
## Day-4 编写models
**有了`ORM`，就可以把`WebApp`需要的表用`Model`表示出来：`models.py`**
- 在编写`ORM`时，给每个`Field`增加一个`default`参数可以让ORM自己填入缺省值，非常方便。并且缺省值可以作为函数对象传入，在调用`save()`时自动计算。
- 比如：定义主键`Id`的缺省值是函数`next_id`,创建时间`created_at`的缺省值是函数`time.time`，可以自动设置当前时间。
- 日期和时间用`float`类型存储在数据库中，而不是`datatime`类型，这么做的好处是不必关心数据库的时区以及时区转换问题，排序非常简便，显示的时候，只需要做一个`float`到`str`的转换。

### 初始化数据库表
1. 连接数据库初始化：脚本见 [`Schema.sql`]( "Schema.sql");
2. 用python的mysql-connector初始化：见 [`InitSchema.py`]( "InitSchema.py").

## Day-5 编写Web框架
> 因为复杂的Web应用程序，光靠一个WSGI(Web Server Gateway Interface)函数来处理还是太底层了，我们需要在WSGI之上再抽象出Web框架(比如Aiohttp、Django、Flask等)，从而进一步简化Web开发。

在Day-1编写web app骨架因为要实现协程，所以运用的是aiohttpweb框架。那么现在为何又要重新编写一个新的web框架呢，这是因为从使用者的角度来说，aiohttp相对比较底层，想要使用框架时编写更少的代码，就只能在aiohttp框架上封装一个更高级的框架。

> Web框架的设计是完全从使用者出发，目的是让框架使用者编写尽可能少的代码。

因此我们希望框架使用者可以摒弃复杂的步骤，这次新创建的框架想要达到的预期效果是：只需编写函数(不然就要创建async def handle_url_xxx(request): ...这样的一大推东西)，透过新建的Web框架就可以实现相同的效果。同时，这样编写简单的函数而非引入request和web.Response还有一个额外的好处，就是可以单独测试，否则，需要模拟一个request才能测试。

因为是以aiohttp框架为基础，要达到上述预期的效果，也是需要符合aiohttp框架要求，因此就需要考虑如何在request对象中，提取使用者编写的函数中需要用到的参数信息，以及如何将函数的返回值转化web.response对象并返回。

### 1. 编写URL处理函数
#### 1.1 aiohttp编写URL处理处理函数
Day-1的URL处理函数比较简单，因为Day-1的的URL处理函数没有真正意义上使用到request参数，但总体上差不多。
使用aiohttp框架，编写一个URL处理函数大概需要几步：
第一步，添加协程装饰器
```
async def handle_url_xxx(request):
       ...
```
第二步，对request参数进行操作，以获取相应的参数
```
url_param = request.match_info['key']
query_params = parse_qs(request.query_string)
```
第三步，就是构造Response对象并返回
```
text = render('template', data)
return web.Response(text.encode('utf-8'))
```
而新创建的web框架希望可以封装以上一些步骤，在使用时，更加方便快捷。

#### 1.2 新建web框架编写URL处理函数
##### 1.2.1 @get 和 @post
> Http定义了与服务器交互的不同方法，最基本的方法有4种，分别是GET，POST，PUT，DELETE。URL全称是资源描述符，我们可以这样认为：一个URL地址，它用于描述一个网络上的资源，而HTTP中的GET，POST，PUT，DELETE就对应着对这个资源的查，改，增，删4个操作。
建议：
> * 1、get方式的安全性较Post方式要差些，包含机密信息的话，建议用Post数据提交方式；
> * 2、在做数据查询时，建议用Get方式；而在做数据添加、修改或删除时，建议用Post方式；

把一个函数映射为一个URL处理函数，可以先构造一个装饰器，用来存储、附带URL信息
##### 1.2.2 定义RequestHandler
> 参考：关于inspect

使用者编写的URL处理函数不一定是一个coroutine，因此用`RequestHandler()`来封装一个**URL**处理函数。
`RequestHandler`是一个类，创建的时候定义了`__call__()`方法，因此可以将其实例视为函数。
`RequestHandler`目的就是从URL函数中分析其需要接收的参数，从request中获取必要的参数，调用URL函数。(要完全符合aiohttp框架的要求，就需要把结果转换为web.Response对象)
##### 1.2.3 封装APIError
从`RequestHandler`代码可以看出最后调用URL函数时，URL函数可能会返回一个名叫`APIError`的错误，那这个APIError又是什么来的呢，其实它的作用是用来返回诸如账号登录信息的错误。

### 2.编写add_route函数以及add_static函数
> 参考：
关于_import_
关于rfind
关于add_static
关于Jinja2

由于新建的web框架时基于aiohttp框架，所以需要再编写一个`add_route()`函数，用来注册一个URL处理函数，主要起验证函数是否有包含URL的响应方法与路径信息，以及将函数变为协程。

通常a`dd_route()`注册会调用很多次，而为了框架使用者更加方便，可以编写了一个可以批量注册的函数`add_routes()`，预期效果是：只需向这个函数提供要批量注册函数的文件路径，新编写的函数就会筛选，注册文件内所有符合注册条件的函数。

`add_static(add):`添加静态文件夹的路径。

`nit_jinja2(app, **kw)`: 添加完静态文件还需要初始化jinja2模板。

### 3. 编写middleware
> 参考：
关于middleware
关于response

如何将函数返回值转化为`web.response`对象呢？

这里引入aiohttp框架的web.Application()中的middleware参数。

middleware是一种拦截器，一个URL在被某个函数处理前，可以经过一系列的middleware的处理。一个middleware可以改变URL的输入、输出，甚至可以决定不继续处理而直接返回。middleware的用处就在于把通用的功能从每个URL处理函数中拿出来，集中放到一个地方。

middleware的感觉有点像装饰器，这与上面编写的RequestHandler有点类似。

从官方文档可以知道，当创建web.appliction的时候，可以设置middleware参数，而middleware的设置是通过创建一些middleware factory(协程函数)。这些middleware factory接受一个app实例，一个handler两个参数，并返回一个新的handler。

- 一个记录URL日志的logger可以作为middle factory；
- 转化得到response对象的middleware factory等。

参考原文链接：[Day5-编写web框架](https://blog.csdn.net/qq_38801354/article/details/73008111 "Day5-编写web框架")

## Day-6 编写配置文件
- 通常，一个`Web App`运行的时候都要读取配置文件，比如数据库的名字，口令等，在不同的环境中运行，可以读取不同的配置文件来获得正确的配置。
- 由于Python本身语法简单，完全可以用源代码来实现配置，而不需要解析一个单独的`.properties` 或者`.yaml`等配置文件。
- 默认的配置文件应该完全符合本地开发环境，这样，无需任何设置，就可以立刻启动服务器。

### 实现思路
1. 编写默认配置文件 `config_default.py`；

2. 编写覆盖配置文件 `config_override.py`；

3. Merge配置文件为`config.py`。

把`config_default.py`作为开发环境的标准配置，把`config_override.py`作为生产环境的标准配置；就可以既方便的在本地开发，又可以随时把应用部署到服务器上。

应用程序读取配置文件需要优先从`config_override.py`读取，为了简化读取配置文件，可以把所有配置读取到统一的`config.py`中。
