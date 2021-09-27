from flask_sqlalchemy import SQLAlchemy

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


# Login Cookie Table ------------------------------------------------
class LoginCookie(db.Model):
    __tablename__ = 'login_cookie'
    cookie = db.Column(db.String, primary_key=True)
