PRAGMA foreign_keys = on;

drop view if exists sys_user_view;

drop table if exists login_cookie;
drop table if exists sys_user;
drop table if exists user_type;


create table user_type(
    id integer primary key not null default 1,
    user_type text unique not null default 'typeless'
);

insert into user_type(user_type) values ('admin'), ('user');

create table sys_user(
    id integer primary key not null default 1,
    user_name text unique not null default 'user_name',
    password text not null default 'password',
    salt text not null default 'salt',
    user_type integer not null default 1,

    constraint sys_user_user_type_fk
                     foreign key(user_type) references user_type(id)
);

insert into sys_user(user_name, password, salt, user_type) values ('root', 'root', 'salt', 1);


create view if not exists sys_user_view as
select sys_user.id as id,
       user_name,
       password,
       salt,
       ut.user_type
from sys_user join user_type ut on sys_user.user_type = ut.id;


create table login_cookie(
    cookie text not null primary key default 'cookie',
    sys_user integer not null default 1,
    expiration_date integer not null default 1,
    constraint login_cookie_sys_user_fk
                         foreign key(sys_user) references sys_user(id)
);


create trigger if not exists new_login_cookie
    after insert
    on login_cookie
begin
    update login_cookie set expiration_date = (strftime('%s', 'now') + 1800) where cookie == New.cookie;
end;