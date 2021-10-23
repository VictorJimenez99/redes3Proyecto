from time import time

from flask import Flask, render_template, make_response, request, redirect
from server.orm import db, SysUser, LoginCookie, RouterUser, Router, RouterProtocol
from server.random import random_word
from server.session import has_valid_session, get_cookie_from_session

app = Flask(__name__)

db_name = 'database.sqlite'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)


# -----------------------------INDEX----------------------------------------------
@app.route('/')
def index():
    if has_valid_session(request):
        print("si es valida")
        return render_template("logged_index.html")
    else:
        return render_template("index.html")

##################################################################################
#                               SESSION                                          #
##################################################################################

# -----------------------------LOGIN----------------------------------------------
@app.route('/login')
def login():
    if has_valid_session(request):
        return redirect("/")
    else:
        return render_template("login.html")


# -----------------------------LOGOUT--------------------------------------
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


# -----------------------------CREATE_SESSION--------------------------------------
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
    user: SysUser
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

##################################################################################
#                               USERS                                            #
##################################################################################
# ----------------------------ADD_SYS_USER----------------------------------------
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
    possible_duplication = SysUser.get_user_by_name(user_name)
    if possible_duplication:
        return "Duplicated user; cannot add new user", 409

    SysUser.add_new_sys_user(user_name, password)

    response = make_response("")
    return response, 200


# -----------------------------CHANGE SysUser EMAIL -------------------------------------------


@app.route('/change_email_sys_user', methods=["POST"])
def change_email_sys_user():
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request):
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    email = payload.get("new_email")
    if email is None:
        return "Unable to get params: Expected json with (new_email)", 406
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if user is None:
        return "Unable to get user_info", 500

    user.change_email_and_commit(email)

    response = make_response("")
    return response, 200


# ---------------------------------Change SysUser Password -------------------------------------

@app.route('/change_password_sys_user', methods=["POST"])
def change_password_sys_user():
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request):
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    new_password = payload.get("new_password")
    if new_password is None:
        return "Unable to get params: Expected json with (new_password)", 406
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if user is None:
        return "Unable to get user_info", 500

    user.change_password_and_commit(new_password)

    LoginCookie.logout_cookie(get_cookie_from_session(request)) # Due to security
    response = make_response("Logged Out")
    return response, 200


##################################################################################
#                               ROUTERS                                          #
##################################################################################
@app.route('/add_router', methods=["POST"])
def add_router():
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request):
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    name = payload.get("name")
    ip_addr = payload.get("ip_addr")
    ip_mask = payload.get("mask")
    protocol = payload.get("protocol")
    if name is None or ip_addr is None or ip_mask is None or protocol is None:
        return "Unable to get params: Expected json with (name, ip_addr, mask, protocol)", 406
    possible_duplication = Router.get_router_by_ip(ip_addr)
    if possible_duplication:
        return "Duplicated router; cannot add new router", 409

    Router.new_router(name, ip_addr, ip_mask, protocol)

    response = make_response("")
    return response, 200









# ----------------------------------MAIN ---------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
