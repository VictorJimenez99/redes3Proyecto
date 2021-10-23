from time import time

from flask_sqlalchemy import SQLAlchemy
from sha3 import sha3_512
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

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

    def get_user_by_id(_user_id: int):
        values: [] = SysUser.query.filter_by(id=_user_id).all()
        if len(values) == 0:
            return []
        return values[0]


    @staticmethod
    def add_new_sys_user(_user_name: str, _password: str):
        user = SysUser(user_name=_user_name)
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
