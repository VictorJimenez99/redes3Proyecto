from flask_sqlalchemy import SQLAlchemy
from sha3 import sha3_512

db = SQLAlchemy()


# Sys User Table -----------------------------------------------------
class SysUser(db.Model):
    __tablename__ = 'sys_user'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String)
    password = db.Column(db.String)
    salt = db.Column(db.String)

    def __repr__(self):
        return f"user {self.id}:\n\tname:{self.user_name}\n\tpassword:{self.salt}\n\tsalt:{self.salt}"

    @staticmethod
    def check_user_exists(_user_name: str):
        values = SysUser.query.filter_by(user_name=_user_name).all()
        return len(values) == 1

    @staticmethod
    def validate_credentials(_user_name, _password):
        user: [] = SysUser.query.filter_by(user_name=_user_name).all()
        if len(user) == 0:
            return False
        # valid user_name
        user: SysUser = user[0]
        test_password: str = _password + user.salt
        print(test_password)
        encrypted_tet = sha3_512(test_password.encode('utf-8')).hexdigest()
        print(encrypted_tet)
        return encrypted_tet


# Login Cookie Table ------------------------------------------------
class LoginCookie(db.Model):
    __tablename__ = 'login_cookie'
    cookie = db.Column(db.String, primary_key=True)
