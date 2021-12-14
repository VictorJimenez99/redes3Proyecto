from datetime import datetime
from time import time

from flask_sqlalchemy import SQLAlchemy
from sha3 import sha3_512
from sqlalchemy import ForeignKey, Column, Integer
from sqlalchemy.orm import relationship

from server.random import random_word

db = SQLAlchemy()

# Log
class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    culprit = db.Column(db.String, default='UNKNOWN USER')
    time = db.Column(db.Integer)
    event = db.Column(db.String, default='UNKNOWN EVENT')
    sent = db.Column(db.Boolean, default=False)

    @staticmethod
    def new_event(event: str, culprit: str):
        value = Log(culprit=culprit, time=0, event=event, sent=False)
        db.session.add(value)
        db.session.commit()

    @staticmethod
    def get_all():
        return Log.query.all()

    @staticmethod
    def get_all_json():
        val = Log.get_all()
        data = []
        for event in val:
            time_str = datetime.utcfromtimestamp(event.time).strftime('%Y-%m-%d %H:%M:%S')
            data.append({"id": event.id,
                         "event": event.event,
                         "culprit": event.culprit,
                         "time_str": time_str,
                         "time_int": event.time,
                         "sent": event.sent})
        return data

    @staticmethod
    def get_not_sent_json():
        val = Log.get_not_sent()
        data = []
        for event in val:
            time_str = datetime.utcfromtimestamp(event.time).strftime('%Y-%m-%d %H:%M:%S')
            data.append({"id": event.id,
                         "event": event.event,
                         "culprit": event.culprit,
                         "time_str": time_str,
                         "time_int": event.time,
                         "sent": event.sent})
        return data

    @staticmethod
    def get_not_sent():
        values: [] = Log.query.filter_by(sent=False).all()
        return values

    @staticmethod
    def change_sent_status(_id, new_status):
        entry = Log.query.filter_by(id=_id).all()
        if len(entry) != 1:
            return
        entry = entry[0]
        setattr(entry, "sent", new_status)
        db.session.commit()




# SysConfig -----------------------------------------
class SysConfig(db.Model):
    __tablename__ = 'sys_config'
    key = db.Column(db.String, primary_key=True)
    value = db.Column(db.String)
    unit = db.Column(db.String)

    def __repr__(self):
        return f"SysConf ({self.key}: {self.value} {self.unit})"

    @staticmethod
    def get_value_of(_key: str):
        values: [] = SysConfig.query.filter_by(key=_key).all()
        if len(values) != 1:
            return None
        conf_item = values[0]
        return conf_item.value

    @staticmethod
    def update_value(_key, _new_value):
        values: [] = SysConfig.query.filter_by(key=_key).all()
        if len(values) != 1:
            return None
        conf_item = values[0]
        setattr(conf_item, "value", _new_value)
        db.session.commit()

    @staticmethod
    def get_all_json():
        val = SysConfig.get_all()
        data = []
        for conf in val:
            data.append({"key": conf.key, "value:": conf.value, "unit": conf.unit})
        return data

    @staticmethod
    def get_all():
        values: [] = SysConfig.query.all()
        if len(values) == 0:
            return []
        return values

    @staticmethod
    def key_exists(_key: str):
        values: [] = SysConfig.query.filter_by(key=_key).all()
        if len(values) != 1:
            return False
        return values[0]


# Sys User Table -----------------------------------------------------
class SysUser(db.Model):
    __tablename__ = 'sys_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String)
    password = db.Column(db.String)
    salt = db.Column(db.String)
    email = db.Column(db.String, default="UNKNOWN")
    user_type = db.Column(db.Integer)

    cookie = relationship("LoginCookie", back_populates="owner_rel", cascade="all,delete")

    def __repr__(self):
        return \
            f"user {self.id}:\n\tname:{self.user_name}" \
            f"\n\tpassword:{self.password}\n\tsalt:{self.salt}\n\temail:{self.email}"

    @staticmethod
    def check_user_exists(_user_name: str):
        values = SysUser.query.filter_by(user_name=_user_name).all()
        return len(values) == 1

    @staticmethod
    def get_user_by_name(_user_name: str):
        values: [] = SysUser.query.filter_by(user_name=_user_name).all()
        if len(values) == 0:
            return []
        return values[0]

    @staticmethod
    def get_all_users():
        values: [] = SysUser.query.all()
        if len(values) == 0:
            return []
        return values

    @staticmethod
    def get_all_emails():
        values: [] = SysUser.query.all()
        if len(values) == 0:
            return []
        values = map(lambda x: x.email, values)
        values = [x for x in values if x != "UNKNOWN"]
        return values

    @staticmethod
    def get_user_by_id(_user_id: int):
        values: [] = SysUser.query.filter_by(id=_user_id).all()
        if len(values) == 0:
            return []
        return values[0]

    @staticmethod
    def drop_user(_id: int):
        user = SysUser.get_user_by_id(_id)
        db.session.delete(user)
        db.session.commit()

    @staticmethod
    def add_new_sys_user(_user_name: str, _password: str, _user_type: int):
        user = SysUser(user_name=_user_name, user_type=_user_type)
        user.salt = random_word(15)

        salted_password: str = _password + user.salt
        encrypted_password = sha3_512(salted_password.encode('utf-8')).hexdigest()
        user.password = encrypted_password
        print(f"adding new user to db: {user}")
        db.session.add(user)
        db.session.commit()

    def change_email_and_commit(self, email: str):
        setattr(self, "email", email)
        print(f"changed {self}")
        db.session.commit()

    def change_password_and_commit(self, new_password: str):
        setattr(self, "salt", random_word(15))
        db.session.commit()

        salted_password: str = new_password + self.salt
        encrypted_password = sha3_512(salted_password.encode('utf-8')).hexdigest()
        setattr(self, "password", encrypted_password)
        db.session.commit()

    def get_dic_info(self):
        dic = {
            "id": self.id,
            "user_name": self.user_name,
            "email": self.email,
        }
        return dic

    @staticmethod
    def validate_credentials(_user_name: str, _password: str):
        user: [] = SysUser.query.filter_by(user_name=_user_name).all()
        if len(user) == 0:
            return False
        # valid user_name
        user: SysUser = user[0]
        test_password: str = _password + user.salt
        encrypted_test = sha3_512(test_password.encode('utf-8')).hexdigest()
        if user.password == encrypted_test:
            return True
        else:
            return False


# Login Cookie Table ------------------------------------------------
class LoginCookie(db.Model):
    __tablename__ = 'login_cookie'
    id = db.Column(db.Integer, primary_key=True)
    cookie = db.Column(db.String, nullable=False)
    expiration_date = db.Column(db.Integer, nullable=False)
    owner = db.Column(db.Integer, ForeignKey('sys_user.id'))

    owner_rel = relationship("SysUser", uselist=False)

    def __repr__(self):
        return f"cookie {self.id}_{self.cookie}: \n\towner: {self.owner}\n\tvalid until: {self.expiration_date}"

    @staticmethod
    def new_cookie(cookie: str, owner: SysUser):
        value = LoginCookie(cookie=cookie, expiration_date=0)
        value.owner = owner.id
        db.session.add(value)
        db.session.commit()

    @staticmethod
    def find_cookie_by_value(cookie: str):
        values: [] = LoginCookie.query.filter_by(cookie=cookie).all()
        if len(values) == 0:
            return None
        return values[0]

    @staticmethod
    def update_cookie(cookie_old_val: str, new_value: str):
        cookie: LoginCookie = LoginCookie.find_cookie_by_value(cookie_old_val)
        setattr(cookie, "cookie", new_value)
        db.session.commit()

    @staticmethod
    def logout_cookie(cookie_val: str):
        cookie: LoginCookie = LoginCookie.find_cookie_by_value(cookie_val)
        setattr(cookie, "expiration_date", int(time()))
        db.session.commit()

    @staticmethod
    def get_owner(cookie_val: str):
        cookie: LoginCookie = LoginCookie.find_cookie_by_value(cookie_val)
        if cookie is None:
            return None
        user_id = cookie.owner
        user = SysUser.get_user_by_id(user_id)
        return user


# Router_connection Table ----------------------------------------------


class RouterConnectionTable(db.Model):
    __tablename__ = 'router_connection'
    source = Column(Integer, ForeignKey("router.id"), primary_key=True)
    source_interface = Column(db.String, default="UNKNOWN")
    destination = Column(Integer, ForeignKey("router.id"), primary_key=True)
    destination_interface = Column(db.String, default="UNKNOWN")
    sent = Column(Integer, default=0)
    received = Column(Integer, default=0)

    def __repr__(self):
        return f"{Router.get_router_by_id(self.source).name}(Interface {self.source_interface}) -> " \
               f"{Router.get_router_by_id(self.destination).name}(Interface {self.destination_interface})"

    @staticmethod
    def new_connection(router1, router2, source_interface, destination_interface):
        connection = RouterConnectionTable(source=router1.id, destination=router2.id,
                                           source_interface=source_interface,
                                           destination_interface=destination_interface)
        print(f"adding new router_connection to db: {connection}")
        db.session.add(connection)
        db.session.commit()

    @staticmethod
    def connection_exists(router1, router2):
        values: [] = RouterConnectionTable.query.filter_by(source=router1.id, destination=router2.id).all()
        if len(values) == 0:
            return None
        return values[0] is not None

    @staticmethod
    def get_connection(router1, router2):
        values: [] = RouterConnectionTable.query.filter_by(source=router1.id, destination=router2.id).all()
        if len(values) == 0:
            return None
        return values[0]

    @staticmethod
    def get_connection_r_i(router1, interface):
        values: [] = RouterConnectionTable.query.filter_by(source=router1.id, source_interface=interface).all()
        if len(values) == 0:
            return None
        return values[0]
    @staticmethod
    def drop_connection(router1, router2):
        conn = RouterConnectionTable.get_connection(router1, router2)
        if conn is None:
            return
        print(f"Deleting router_connection: {conn}")
        db.session.delete(conn)
        db.session.commit()

    def update_interfaces(self, interface_source: str, interface_dest: str):
        setattr(self, 'source_interface', interface_source)
        setattr(self, 'destination_interface', interface_dest)
        db.session.commit()

    def update_sent(self, sent: int):
        setattr(self, 'sent', sent)
        db.session.commit()

    def update_received(self, received: int):
        setattr(self, 'received', received)
        db.session.commit()

    @staticmethod
    def get_all():
        values: [] = RouterConnectionTable.query.all()
        if len(values) == 0:
            return []
        return values


# Router Table ------------------------------------------------

class Router(db.Model):
    __tablename__ = 'router'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    ip_addr = db.Column(db.String, nullable=False)
    protocol = db.Column(db.String, nullable=False)
    sys_name = db.Column(db.String, default="UNKNOWN")
    sys_contact = db.Column(db.String, default="UNKNOWN")
    sys_location = db.Column(db.String, default="UNKNOWN")
    needs_snmp_update = db.Column(db.Boolean, default=False)
    needs_snmp_read = db.Column(db.Boolean, default=False)

    router_conn_sources_rel = relationship("Router",
                                           secondary="router_connection",
                                           primaryjoin="(Router.id==RouterConnectionTable.destination)",
                                           secondaryjoin="(Router.id==RouterConnectionTable.source)",
                                           backref=db.backref("router_dest_rel", lazy='dynamic'))

    def unset_for_update(self):
        setattr(self, 'needs_snmp_update', False)
        db.session.commit()

    def set_for_update(self):
        setattr(self, 'needs_snmp_update', True)
        db.session.commit()

    def set_for_read(self):
        setattr(self, 'needs_snmp_read', True)
        db.session.commit()

    def unset_for_read(self):
        setattr(self, 'needs_snmp_read', False)
        db.session.commit()

    def set_to_update_sys_name(self, new_name):
        setattr(self, 'sys_name', new_name)
        setattr(self, "needs_snmp_update", True)
        db.session.commit()

    def set_to_update_sys_contact(self, new_contact):
        setattr(self, 'sys_contact', new_contact)
        setattr(self, "needs_snmp_update", True)
        db.session.commit()

    def set_to_update_sys_location(self, new_location):
        setattr(self, 'sys_location', new_location)
        setattr(self, "needs_snmp_update", True)
        db.session.commit()

    @staticmethod
    def get_router_that_need_snmp_read():
        values: [] = Router.query.filter_by(needs_snmp_read=True).all()
        if len(values) == 0:
            return None
        return values

    @staticmethod
    def get_snmp_values(router_name):
        router = Router.get_router_by_name(router_name)
        if router is None:
            return None
        return {"sys_name": router.sys_name,
                "sys_contact": router.sys_contact,
                "sys_location": router.sys_location}


    @staticmethod
    def get_router_that_need_snmp_update():
        values: [] = Router.query.filter_by(needs_snmp_update=True).all()
        if len(values) == 0:
            return None
        return values

    def __repr__(self):
        return f"[id: {self.id}, name: {self.name}, ip_addr: {self.ip_addr}, protocol: {self.protocol}]"

    @staticmethod
    def new_router(router_name: str, ip_addr: str, protocol: str):
        router = Router(name=router_name, ip_addr=ip_addr, protocol=protocol)
        print(f"adding new router to db: {router}")
        db.session.add(router)
        db.session.commit()

    def change_name(self, router_name: str):
        setattr(self, 'name', router_name)
        db.session.commit()

    def change_ip_addr(self, ip_addr: str):
        setattr(self, 'ip_addr', ip_addr)
        db.session.commit()

    def change_protocol(self, protocol: str):
        setattr(self, 'protocol', protocol)
        db.session.commit()

    @staticmethod
    def get_connections_of(router_id):
        values: [] = RouterConnectionTable.query.filter_by(source=router_id).all()
        if len(values) == 0:
            return None
        return values

    @staticmethod
    def get_router_by_name(_name: str):
        values: [] = Router.query.filter_by(name=_name).all()
        if len(values) == 0:
            return None
        return values[0]

    @staticmethod
    def get_router_by_id(_id: int):
        values: [] = Router.query.filter_by(id=_id).all()
        if len(values) == 0:
            return None
        return values[0]

    @staticmethod
    def get_router_by_ip(_ip: str):
        values: [] = Router.query.filter_by(ip_addr=_ip).all()
        if len(values) == 0:
            return None
        return values[0]

    @staticmethod
    def get_router_all():
        values: [] = Router.query.all()
        if len(values) == 0:
            return []
        return values

    @staticmethod
    def drop_router(_id: int):
        router = Router.get_router_by_id(_id)
        print(f"Deleting router: {router}")
        db.session.delete(router)
        db.session.commit()



# Router Users  Table ----------------------------------------------

class RouterUser(db.Model):
    __table_name__ = 'router_user'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    salt = db.Column(db.String, nullable=False)
    user_type = db.Column(db.Integer, nullable=False)

    @staticmethod
    def new_user_router(user_name: str, password: str, user_type: str):
        user_router = RouterUser(user_name=user_name, user_type=user_type)
        user_router.salt = random_word(15)
        salted_password: str = password + user_router.salt
        encrypted_password = sha3_512(salted_password.encode('utf-8')).hexdigest()
        user_router.password = encrypted_password
        print(f"adding a new user router {user_router}")
        db.session.add(user_router)
        db.session.commit()

    def change_password(self, _password: str):
        salted_password: str = _password + self.salt
        encrypted_password = sha3_512(salted_password.encode('utf-8')).hexdigest()
        setattr(self, "password", encrypted_password)
        db.session.commit()

    def change_user_type(self, user_type: int):
        print(user_type)
        setattr(self, "user_type", user_type)
        db.session.commit()

    @staticmethod
    def drop_user_router(_id: int):
        router_user = RouterUser.get_router_user_by_id(_id)
        db.session.delete(router_user)
        db.session.commit()

    @staticmethod
    def get_router_user_by_name(_name: str):
        values: [] = RouterUser.query.filter_by(user_name=_name).all()
        if len(values) == 0:
            return None
        return values[0]

    @staticmethod
    def get_router_user_by_id(_id: int):
        values: [] = RouterUser.query.filter_by(id=_id).all()
        if len(values) == 0:
            return None
        return values[0]

    @staticmethod
    def get_all_users():
        values: [] = RouterUser.query.all()
        if len(values) == 0:
            return []
        return values

    @staticmethod
    def validate_credentials(_user_name: str, _password: str):
        user: [] = RouterUser.query.filter_by(user_name=_user_name).all()
        if len(user) == 0:
            return False
        # valid user_name
        user: RouterUser = user[0]
        test_password: str = _password + user.salt
        encrypted_test = sha3_512(test_password.encode('utf-8')).hexdigest()
        if user.password == encrypted_test:
            return True
        else:
            return False


# Protocol   ----------------------------------------------------------

class RouterProtocol(db.Model):
    __table_name__ = 'router_protocol'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    @staticmethod
    def new_router_protocol(protocol_name: str):
        router_protocol = RouterProtocol(name=protocol_name)
        db.session.add(router_protocol)
        db.session.commit()

    @staticmethod
    def get_protocol_by_id(_id: int):
        values: [] = RouterProtocol.query.filter_by(id=_id).all()
        if len(values) == 0:
            return None
        return values[0]

    @staticmethod
    def get_protocol_by_name(_name: str):
        values: [] = RouterProtocol.query.filter_by(name=_name).all()
        if len(values) == 0:
            return None
        return values[0]

    @staticmethod
    def drop_router_protocol(_id: int):
        router_protocol = RouterProtocol.get_router_user_by_id(_id)
        db.session.delete(router_protocol)
        db.session.commit()
