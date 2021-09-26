PRAGMA foreign_keys = on;

drop view if exists sys_user_view;

drop table if exists login_cookie;
drop table if exists sys_user;
drop table if exists user_type;


create table user_type(
    id integer primary key not null default 1,
    user_type text unique not null default 'typeless'
);

create table sys_user(
    id integer primary key not null default 1,
    user_name text unique not null default 'user_name',
    password text not null default 'password',
    salt text not null default 'salt',
    user_type integer not null default 1,

    constraint sys_user_user_type_fk
                     foreign key(user_type) references user_type(id)
);


create view if not exists sys_user_view as
select id,
       user_name,
       password,
       salt,
       user_type from sys_user join user_type ut on sys_user.user_type = ut.id;


create table login_cookie(
    cookie text not null primary key default 'cookie',
    sys_user integer not null default 1,
    expiration_date integer not null default 0,
    constraint login_cookie_sys_user_fk
                         foreign key(sys_user) references sys_user(id)
);
