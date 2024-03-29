PRAGMA foreign_keys = ON;

drop table if exists login_cookie;
drop table if exists sys_user;


create table user_type
(
    id        integer primary key not null default 1,
    user_type text unique         not null default 'typeless'
);


create table log
(
    id  integer primary key not null default 1,
    culprit text not null default 'UNKNOWN USER',
    time integer not null default 0,
    event text not null default 'UNKNOWN EVENT',
    sent boolean not null default false
);

create trigger if not exists insert_new_log
    after insert
    on log
begin
update log set time = strftime('%s', 'now') where id == New.id;
end;

create table sys_user
(
    id        integer primary key not null default 1,
    user_name text unique         not null default 'user_name',
    password  text                not null default 'password',
    salt      text                not null default 'salt',
    email     text                not null default 'no_email',
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



insert into sys_user(user_name, password, salt, email,user_type)
values ('root',
        '4aa15c394ae968cee7ed66134ef24d6e34a323a5aaed9d5d6095e71da60c55aad51b3974562c50db79c15ba37a2c3ea2a096e6581a562356a5783ab9a6732605',
        'salt', 'jimenezvictor99@gmail.com',1);



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
    id       integer    not null primary key default 0,
    name     text       unique not null                    default 'no name',
    ip_addr  text       not null unique                    default '0.0.0.0',
    protocol text       not null,
    sys_name text       not null default 'UNKNOWN',
    sys_location text   not null default 'UNKNOWN',
    sys_contact text    not null default 'UNKNOWN',
    needs_snmp_update boolean not null default false,
    needs_snmp_read boolean not null default false
);

create table router_protocol
(
    id   integer not null primary key default 0,
    name text    not null
);

create table router_connection
(
  source  integer not null,
  source_interface text not null default 'UNKNOWN',
  destination integer not null,
  destination_interface text not null default 'UNKNOWN',
  sent integer not null default 0,
  received integer not null default 0,
  primary key(source, destination),
  constraint  router_connection_source_fk
      foreign key (source) references router(id) on delete cascade,
  constraint  router_connection_destination_fk
      foreign key (destination) references router(id) on delete cascade
);

create view if not exists router_connection_view as
select r.id as source_id,
       r.name as source_name,
       r2.id as destination_id,
       r2.name as destination_name
from router_connection as rel
         join router r on rel.source = r.id
         join  router r2 on rel.destination = r2.id;


create table sys_config
(
    key text primary key not null,
    value text not null,
    unit text not null
);


insert into sys_config values
                              ('topology_test_await_time', '100', 'seconds'),
                              ('snmp_client_read_await_time', '30', 'seconds'),
                              ('smtp_client_await_time_mail', '10', 'seconds'),
                              ('snmp_client_update_await_time', '30', 'seconds'),
                              ('snmp_packets_await_time', '10', 'seconds');







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

/*
insert into router(name, ip_addr, protocol)
values ('R1.red1.com', '10.1.0.254', '1'),
       ('R7.red7.com', '10.2.0.252', '1'),
       ('R2.red2.com', '10.2.0.251', '1'),
       ('R6.red5.com', '10.2.0.241', '1'),
       ('R5.red7.com', '10.2.0.242', '1'),
       ('R8.red6.com', '10.2.0.243', '1'),
       ('R3.red3.com', '10.2.0.244', '1'),
       ('R4.red4.com', '10.7.0.245', '1');
insert into router_connection(source, destination)
values (1,2), (1,3), (1,4),
       (2,1), (2,5), (2,6),
       (3,7), (3,1),
       (4,8), (4,7), (4, 1),
       (5,2), (5,7),
       (6,2),
       (7,3), (7,5), (7,4),
       (8,4);
 */
insert into router_user(user_name, password, salt, user_type)
values ('root',
        '4aa15c394ae968cee7ed66134ef24d6e34a323a5aaed9d5d6095e71da60c55aad51b3974562c50db79c15ba37a2c3ea2a096e6581a562356a5783ab9a6732605',
        'salt', 15);