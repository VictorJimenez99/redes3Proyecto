PRAGMA foreign_keys = ON;

drop table if exists login_cookie;
drop table if exists sys_user;


create table user_type
(
    id        integer primary key not null default 1,
    user_type text unique         not null default 'typeless'
);

create table sys_user
(
    id        integer primary key not null default 1,
    user_name text unique         not null default 'user_name',
    password  text                not null default 'password',
    salt      text                not null default 'salt',
    email     text,
    user_type integer             not null default 1,

    constraint sys_user_user_type_fk
        foreign key (user_type) references user_type (id)
);

create view if not exists sys_user_view as
select sys_user.id,
       user_name,
       password,
       salt,
       ut.user_type
from sys_user
         join user_type ut on sys_user.user_type = ut.id;



insert into user_type(id, user_type)
values (1,
        'admin');

insert into user_type(id, user_type)
values (2,
        'normal');



insert into sys_user(user_name, password, salt, user_type)
values ('root',
        '4aa15c394ae968cee7ed66134ef24d6e34a323a5aaed9d5d6095e71da60c55aad51b3974562c50db79c15ba37a2c3ea2a096e6581a562356a5783ab9a6732605',
        'salt', 1);



create table login_cookie
(
    id              integer not null primary key default 0,
    cookie          text    not null             default 'cookie',
    owner           integer not null             default 1,
    expiration_date integer not null             default 1,
    constraint login_cookie_sys_user_fk
        foreign key (owner) references sys_user (id) on delete cascade on update restrict
);


create trigger if not exists new_login_cookie
    after insert
    on login_cookie
begin
    update login_cookie set expiration_date = (strftime('%s', 'now') + 1800) where id == New.id;
end;

create table router_user_type
(
    id        integer primary key not null default 1,
    user_type text unique         not null default 'typeless'
);

create table router_user
(
    id        integer not null primary key,
    user_name text    not null default 'no name',
    password  text    not null default 'password',
    salt      text    not null default 'salt',
    user_type integer not null default 2,

    constraint router_user_user_type_fk
        foreign key (user_type) references router_user_type (id)

);

create table router
(
    id       integer     not null primary key default 0,
    name     text        unique not null                    default 'no name',
    ip_addr  text        not null unique                    default '0.0.0.0',
    protocol text        not null,
    protocol_name text        default null
);

create table router_protocol
(
    id   integer not null primary key default 0,
    name text    not null
);

create table router_connection
(
  router  integer not null,
  connected_to integer not null,
  primary key(router, connected_to),
  constraint  router_is_connected_to_parent_fk
      foreign key (router) references router(id),
  constraint  router_is_connected_to_child_fk
      foreign key (router) references router(id)
);

create view if not exists router_connection_view as
select r.id as router,
       r.name as name,
       r2.id as other_id,
       r2.name as other_name
from router_connection as rel
         join router r on rel.router = r.id
         join  router r2 on rel.connected_to = r2.id;

insert into router_protocol(name)
values ('RIP');
insert into router_protocol(name)
values ('OSPF');
insert into router_protocol(name)
values ('IGRP');


insert into router_user_type(id, user_type)
values (0,'lectura');

insert into router_user_type(id, user_type)
values (15,
        'admin');

insert into router(name, ip_addr, protocol, protocol_name)
values ('R1','10.0.2.254','2','1');


insert into router(name, ip_addr, protocol, protocol_name)
values ('R2','10.0.3.2','2','1');

insert into router_connection
values (1,2), (2,1);


insert into router_user(user_name, password, salt, user_type)
values ('root',
        '4aa15c394ae968cee7ed66134ef24d6e34a323a5aaed9d5d6095e71da60c55aad51b3974562c50db79c15ba37a2c3ea2a096e6581a562356a5783ab9a6732605',
        'salt', 15);