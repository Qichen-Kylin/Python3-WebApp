# Python3-WebApp
基于Python3的Web开发

# WebApp实战
##  Day-1 搭建开发环境
***2019-11-19 星期二***
1. 确认当前系统安装的Python版本：
```Markdown
(base) C:\Windows\system32&gt;python --version
Python 3.6.5 :: Anaconda, Inc.
```

2. 安装MySQL数据库：从[MySQL官方网站](https://dev.mysql.com/downloads/mysql/5.6.html &quot;MySQL官方网站&quot;)下载并安装。

3. 然后，用`pip`安装开发Web App需要的第三方库：
 - **异步框架 aiohttp:** `pip install aiohttp`
 - **前端模板引擎 jinja2:** `pip install jinja2`
 - **MySQL的python异步驱动程序aiomysql：** `pip install aiomysql`

4. 项目结构
选择一个工作目录，建立大致如下的目录结构：
```Markdown
python3-webapp/  &lt;-- 根目录
|
+- backup/       &lt;-- 备份目录
|
+- conf/         &lt;-- 配置文件
|
+- dist/         &lt;-- 打包目录
|
+- www/          &lt;-- Web目录，存放.py文件
| |
| +- static/     &lt;-- 存放静态文件
| |
| +- templates/  &lt;-- 存放模板文件
|
+- LICENSE       &lt;-- 代码LICENSE
```
创建好工作目录结构后，建立**Git仓库**并同步至[`GitHub`](https://github.com/Qichen-Kylin/Python3-WebApp &quot;Qichen-Kylin/Python3-WebApp&quot;)，版本控制保证代码修改安全:
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
