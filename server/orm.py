from time import time

from flask_sqlalchemy import SQLAlchemy
from sha3 import sha3_512
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, sessionmaker

from server.random import random_word

db = SQLAlchemy()


# Sys User Table -----------------------------------------------------
class SysUser(db.Model):
    __tablename__ = 'sys_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String)
    password = db.Column(db.String)
    salt = db.Column(db.String)
    email = db.Column(db.String)
    user_type = db.Column(db.Integer)

    cookie = relationship("LoginCookie", back_populates="owner_rel")

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
    def add_new_sys_user(_user_name: str, _password: str,_user_type: int):
        user = SysUser(user_name=_user_name, user_type = _user_type)
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
        user_id = cookie.owner
        user = SysUser.get_user_by_id(user_id)
        return user


# Router Table ------------------------------------------------

class Router(db.Model):
    __table_name__ = 'router'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    ip_addr = db.Column(db.String, nullable=False)
    protocol = db.Column(db.String, nullable=False)

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
        user_router = RouterUser(user_name=user_name, user_type = user_type)
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
    def get_router_user_by_id(_id: int):
        values: [] = RouterProtocol.query.filter_by(id=_id).all()
        if len(values) == 0:
            return None
        return values[0]

    @staticmethod
    def drop_router_protocol(_id: int):
        router_protocol = RouterProtocol.get_router_user_by_id(_id)
        db.session.delete(router_protocol)
        db.session.commit()
