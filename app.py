from time import time

from flask import Flask, render_template, make_response, request, redirect
from server.orm import db, SysUser, LoginCookie
from server.random import random_word
from server.session import has_valid_session

app = Flask(__name__)

db_name = 'database.sqlite'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)


@app.route('/')
def index():
    if has_valid_session(request):
        print("si es valida")
        return render_template("logged_index.html")
    else:
        return render_template("index.html")


@app.route('/login')
def login():
    if has_valid_session(request):
        return redirect("/")
    else:
        return render_template("login.html")


@app.route('/create_session', methods=["POST"])
def set_cookie():
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415

    if has_valid_session(request):
        return "Already Reported", 208

    payload: dict = request.get_json(force=True)
    user_name = payload.get("name")
    password = payload.get("password")
    user: SysUser = SysUser()
    if SysUser.validate_credentials(user_name, password):
        user = SysUser.get_user_by_name(user_name)
    else:
        return "Invalid_Credentials", 418

    random_string = random_word(15)

    cookie = f"{user.user_name}{random_string}{int(time())}"
    LoginCookie.new_cookie(cookie, user)

    response = make_response("")
    response.set_cookie("access_key", cookie)

    return response, 200


@app.route('/check_cookie')
def has_cookie():
    value = request.cookies.get('login')
    return f"login {value}"

@app.route('/logout', methods=["POST"])
def logout():
    if request.method != 'POST':
        return "not a post method", 400
    if not has_valid_session(request):
        return "Already logout", 208
    response = make_response("")
    value = request.cookies.get('access_key')
    LoginCookie.logout_cookie(value)
    response.delete_cookie('access_key')
    return response, 200


@app.route('/add_sys_user', methods=["POST"])
def add_sys_user():
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request):
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    user_name = payload.get("new_name")
    password = payload.get("new_password")
    if user_name is None or password is None:
        return "Unable to get params: Expected json with (new_name, new_password)", 406
    SysUser.add_new_sys_user(user_name, password)

    response = make_response("")
    return response, 200


if __name__ == '__main__':
    app.run(debug=True)
