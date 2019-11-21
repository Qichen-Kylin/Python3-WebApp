# Python3-WebApp
基于Python3的Web开发

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

**------------**
- **协程（Coroutine）**
1. 协程，又称微线程。协程看上去也是子程序，但是执行过程中，在子程序内部可以中断，然后转而执行别的子程序，在适当的时间再返回来接着执行中断的子程序。

2. 协程的特点在于是一个线程执行，和多线程相比协程最大的优势就是极高的执行效率。因为子程序切换不是线程切换，而是程序自身控制，因此，没有线程切换的开销，和多线程比，线程数量越多，协程的性能优势就越明显；第二大优势就是不需要多线程的锁机制，因为只有一个线程，也不存在同时写变量冲突，在协程中控制共享资源不加锁，只需要判断状态就好了，所以执行效率比多线程高很多。

3. Python对协程的支持是通过`generator`实现的。在generator中，不但可以通过循环来迭代，还可以不断的调用`next()`函数获取有`yield`语句返回的下一个值。Python的yield还可以接收调用者发出的参数。

- **asyncio**
1. `asyncio`是直接内置对异步IO的支持。`asyncio`的编程模型就是一个消息循环。我们从`asyncio`模块中直接获取一个`EventLoop`的引用，然后把需要执行的`协程`扔到`EventLoop`中执行，就实现了异步IO。

2. `asyncio`提供了完善的的异步IO支持；异步操作需要在`coroutine(协同程序)`中通过`yield from`完成；多个`coroutine`可以分装成一组Task然后并发执行。

3. `asyncio`可以实现单线程并发IO操作。如果将其只用在客户端，则发挥的威力不大；如果将它放在服务器端，例如Web服务器，由于http连接就是IO操作，因此可以用`单线程+协程`实现多用户的高并发支持。
