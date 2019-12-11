#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'kylin'

import mysql.connector

conn = mysql.connector.connect(user='webapp', password='123456', database='webapp')#连接MySQL数据库中的webapp数据库
cursor = conn.cursor() #创建游标
cursor.execute('create table users (id varchar(50) primary key,email varchar(50),passwd varchar(50),name varchar(50),image varchar(500),admin boolean,create_at real)')#创建users表-->表列都要定义名字及类型，主键后还要跟primary key
cursor.execute('create table blogs (id varchar(50) primary key,user_id varchar(50),user_name varchar(50),user_image varchar(500),name varchar(50),summary varchar(200),content text,create_at real)')#创建blogs表
cursor.execute('create table comments (id varchar(50) primary key,blog_id varchar(50),user_id varchar(50),user_name varchar(50),user_image varchar(500),content text,create_at real)')#创建comments表
cursor.close()
conn.commit()
conn.close()