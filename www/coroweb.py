#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Kylin'

import asyncio, os, inspect, logging, functools

from urllib import parse

from aiohttp import web

from apis import APIError

'''
把一个函数映射成一个URL处理函数，可以先构造一个装饰器，用来存储、附带URL信息。
通过@get()、@post()装饰就附带URL信息。
'''
def get(path):
    '''
    Define decorator @get('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator

def post(path):
    '''
    Define decorator @post('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator

#运用inspect模块，创建几个函数用以获取URL处理函数与request参数之间的关系：
def get_required_kw_args(fn):  #收集没有默认值的命名关键字参数
    args = []
    params = inspect.signature(fn).parameters  #inspect模块是用来分析模块，函数
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)

def get_named_kw_args(fn):  #获取命名关键字参数
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)

def has_named_kw_args(fn):  #判断有没有命名关键字参数
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True

def has_var_kw_arg(fn):  #判断有没有关键字参数
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True

def has_request_arg(fn):  #判断是否含有名叫'request'参数，且该参数是否为最后一个参数
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False
    for name, param in params.items():
        if name == 'request':
            found = True
            continue  #跳出当前循环，进入下一个循环
        if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError('request parameter must be the last named parameter in function: %s%s' % (fn.__name__, str(sig)))
    return found
'''
定义请求处理器：正式向request参数获取URL处理函数所需的参数。
URL处理函数不一定就是一个协同程序（`coroutine`），因此用`RequestHandler()`来封装一个URL处理函数。
`RequestHandler`是一个类，由于定义了`__call__()`方法，因此可以将其实例视为函数。
`RequestHandler`目的就是从URL函数中分析其需要接收的参数,从request中获取必要的参数；调用URL函数，然后把结果转换为web.Response对象。
因此，完全符合aiohttp的框架的要求。
'''
class RequestHandler(object):

    def __init__(self, app, fn):  #接受app参数
        self._app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)

    async def __call__(self, request):  #__call__这里要构造协程
        kw = None
        if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
            if request.method == 'POST':  #判断客户端发来的方法是否为POST
                if not request.content_type:  #查询有没提交数据的格式（EncType）
                    #return web.HTTPBadRequest('Missing Content-Type.')
                    return web.HTTPBadRequest(text='Missing Content-Type.') #要有text
                ct = request.content_type.lower() #转换为小写
                if ct.startswith('application/json'):
                    params = await request.json()  #Read request body decoded as json.
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest(text='JSON body must be object.')
                    kw = params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    '''
                    reads POST parameters from request body.
                    If method is not POST, PUT, PATCH, TRACE or DELETE or content_type is not empty 
                    or application/x-www-form-urlencoded or multipart/form-data returns empty multidict.
                    '''
                    params = await request.post() 
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest(text='Unsupported Content-Type: %s' % request.content_type)
            if request.method == 'GET':
                qs = request.query_string  #The query string in the URL
                if qs:
                    kw = dict()
                    '''
                    Parse a query string given as a string argument.Data are returned as a dictionary. 
                    The dictionary keys are the unique query variable names and the values are lists of values for each name.
                    '''
                    for k, v in parse.parse_qs(qs, True).items():
                        kw[k] = v[0]
        if kw is None:
            kw = dict(**request.match_info)
        else:
            if not self._has_var_kw_arg and self._named_kw_args: #当函数参数没有关键字参数时，移去request除命名关键字参数所有的参数信息
                # remove all unamed kw:
                copy = dict()
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            # check named arg:
            for k, v in request.match_info.items():  #检查命名关键参数
                if k in kw:
                    logging.warning('Duplicate arg name in named arg and kw args: %s' % k)
                kw[k] = v
        if self._has_request_arg:
            kw['request'] = request
        # check required kw:
        if self._required_kw_args: #假如命名关键字参数(没有附加默认值)，request没有提供相应的数值，报错
            for name in self._required_kw_args:
                if not name in kw:
                    return web.HTTPBadRequest(text='Missing argument: %s' % name)
        logging.info('call with args: %s' % str(kw))
        try:
            r = await self._func(**kw)
            return r
        except APIError as e:  #APIError另外创建
            return dict(error=e.error, data=e.data, message=e.message)
'''
添加静态文件夹的路径:
'''
def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static') #输出当前文件夹中'static'的路径
    app.router.add_static('/static/', path)
    logging.info('add static %s => %s' % ('/static/', path))

'''
add_route():用来注册一个URL处理函数。
主要起验证函数是否有包含URL的响应方法与路径信息，以及将函数变为协程。
'''
def add_route(app, fn):
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):  #判断是否为协程且生成器
        fn = asyncio.coroutine(fn)
    logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn)) #RequestHandler的参数有两个

'''
add_routes()批量注册函数：把很多次add_route()注册的调用，变成自动扫描；
预期效果是：只需向这个函数提供要批量注册函数的文件路径，新编写的函数就会筛选，注册文件内所有符合注册条件的函数。
所以就是，自动把Handler模块的所有符合条件的函数都注册了。
'''
def add_routes(app, module_name):
    n = module_name.rfind('.')
    if n == (-1):
        mod = __import__(module_name, globals(), locals())
    else:
        name = module_name[n+1:]
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)  #第一个参数为文件路径参数，不能掺夹函数名，类名
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        fn = getattr(mod, attr)
        if callable(fn):
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            if method and path:  #这里要查询path以及method是否存在而不是等待add_route函数查询，因为那里错误就要报错了
                add_route(app, fn)