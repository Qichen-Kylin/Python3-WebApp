--schema.sql

--mysql -u root --password='123456' -e "create user 'WebApp'@'%' identified by '123456'"
--create user 'webapp'@'%' identified by '123456';

drop database if exists webapp;
--mysql -u root --password='123456' -e "create database webapp default character set utf8"
create database webapp default character set utf8;

--mysql -u root --password='123456' -e "grant all privileges on webapp.* to 'webapp'@'%'"
grant select,insert,update,delete on webapp.* to 'webapp'@'%';

use webapp;

create table users (
    id varchar(50) not null,
    email varchar(50) not null,
    passwd varchar(50) not null,
    admin bool not null,
    name varchar(50) not null,
    image varchar(500) not null,
    created_at real not null,
    unique key idx_email (email),
    key idx_created_at (created_at),
    primary key (id)
) engine=innodb default charset=utf8;

create table blogs (
    id varchar(50) not null,
    user_id varchar(50) not null,
    user_name varchar(50) not null,
    user_image varchar(500) not null,
    name varchar(50) not null,
    summary varchar(200) not null,
    content mediumtext not null,
    created_at real not null,
    key idx_created_at (created_at),
    primary key (id)
) engine=innodb default charset=utf8;

create table comments (
    id varchar(50) not null,
    blog_id varchar(50) not null,
    user_id varchar(50) not null,
    user_name varchar(50) not null,
    user_image varchar(500) not null,
    content mediumtext not null,
    created_at real not null,
    key idx_created_at (created_at),
    primary key (id)
) engine=innodb default charset=utf8;

/*
1、 mysql> source /Schema.sql
2、 # mysql -u root --password='123456' < Schema.sql
 */