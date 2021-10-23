PRAGMA foreign_keys = on;

drop table if exists login_cookie;
drop table if exists sys_user;



create table sys_user
(
    id        integer primary key not null default 1,
    user_name text unique         not null default 'user_name',
    password  text                not null default 'password',
    salt      text                not null default 'salt',
    email     text
);

insert into sys_user(user_name, password, salt)
values ('root',
        '4aa15c394ae968cee7ed66134ef24d6e34a323a5aaed9d5d6095e71da60c55aad51b3974562c50db79c15ba37a2c3ea2a096e6581a562356a5783ab9a6732605',
        'salt');



create table login_cookie
(
    id              integer not null primary key default 0,
    cookie          text    not null             default 'cookie',
    owner           integer not null             default 1,
    expiration_date integer not null             default 1,
    constraint login_cookie_sys_user_fk
        foreign key (owner) references sys_user (id)
);


create trigger if not exists new_login_cookie
    after insert
    on login_cookie
begin
    update login_cookie set expiration_date = (strftime('%s', 'now') + 1800) where id == New.id;
end;

create table router_user
(
    id        integer not null  primary key autoincrement,
    user_name text    not null default 'no name',
    password  text    not null default 'password',
    salt      text    not null default 'salt'

);

create table router
(
    id       integer not null primary key autoincrement default 0,
    name     text  unique  not null             default 'no name',
    ip_addr  text    not null  unique     default '0.0.0.0',
    protocol text    not null
);

create table router_protocol(
    id integer not null primary key autoincrement default 0,
    name text not null
)
