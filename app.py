from time import time

from flask import Flask, render_template, make_response, request, redirect, jsonify
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


# -----------------------------View SysUser update -------------------------------------------
@app.route('/app_user_pass')
def app_user():
    if has_valid_session(request):
        return render_template("user/app_user_pass.html")
    else:
        return redirect("/")


# -----------------------------View SysUser update -------------------------------------------
@app.route('/app_user_list')
def app_user_list():
    if has_valid_session(request):
        users = SysUser.get_all_users()
        return render_template("user/app_user_list.html", len=len(users), users=users)
    else:
        return redirect("/")

# -----------------------------View SysUser add -------------------------------------------
@app.route('/add_view_sys_user')
def add_view_sys_user():
    if has_valid_session(request):
        return render_template("user/add_view_sys_user.html")
    else:
        return redirect("/")


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

    LoginCookie.logout_cookie(get_cookie_from_session(request))  # Due to security
    response = make_response("Logged Out")
    return response, 200


# -----------------------------GET SysUser -------------------------------------------


@app.route('/get_sysuser_info', methods=["POST"])
def get_sysuser_info():
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request):
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    response = make_response(jsonify(user.get_dic_info()))
    return response, 200


##################################################################################
#                               ROUTERS                                          #
##################################################################################




# ---------------------------------add Router  -------------------------------------

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
    protocol = payload.get("protocol")
    if name is None or ip_addr is None or protocol is None:
        return "Unable to get params: Expected json with (name, ip_addr, protocol)", 406
    possible_duplication = Router.get_router_by_ip(ip_addr)
    if possible_duplication:
        return "Duplicated router; cannot add new router", 409

    Router.new_router(name, ip_addr, protocol)

    response = make_response("")
    return response, 200


# ---------------------------------Update Router  -------------------------------------

@app.route('/update_router', methods=["POST"])
def update_router():
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request):
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    id = payload.get("id")
    name = payload.get("name")
    ip_addr = payload.get("ip_addr")
    protocol = payload.get("protocol")
    if id is None or name is None or ip_addr is None or protocol is None:
        return "Unable to get params: Expected json with (id, name, ip_addr, protocol)", 406
    router: Router = Router.get_router_by_id(id)
    if router is None:
        return "Unable to get router_info", 500

    router.change_name(name)
    router.change_ip_addr(ip_addr)
    router.change_protocol(protocol)
    response = make_response("")
    return response, 200


# ---------------------------------Drop Router User  -------------------------------------

@app.route('/drop_router', methods=["POST"])
def drop_router():
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request):
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    id = payload.get("id")
    if id is None:
        return "Unable to get params: Expected json with (id)", 406
    router: Router = Router.get_router_by_id(id)
    if router is None:
        return "Unable to get router_user_info", 500
    router.drop_router(id)
    response = make_response("")
    return response, 200


##################################################################################
#                               ROUTERS USERS                                    #
##################################################################################

# ---------------------------------View List Router User  -------------------------------------
@app.route('/router_user_list')
def router_user_list():
    if has_valid_session(request):
        users = RouterUser.get_all_users()
        return render_template("user_router/router_user_list.html", len=len(users), users=users)
    else:
        return redirect("/")


# ---------------------------------Add Router User  -------------------------------------

@app.route('/add_router_user', methods=["POST"])
def add_router_user():
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request):
        print(get_cookie_from_session(request))

        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    name = payload.get("user_name")
    password = payload.get("password")
    if name is None or name is None or password is None:
        return "Unable to get params: Expected json with (user_name, password)", 406
    possible_duplication = RouterUser.get_router_user_by_name(name)
    if possible_duplication:
        return "Duplicated router user; cannot add new user router", 409
    RouterUser.new_user_router(name, password)

    response = make_response("")
    return response, 200


# ---------------------------------Update Router User  -------------------------------------

@app.route('/update_router_user', methods=["POST"])
def update_router_user():
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request):
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    id = payload.get("id")
    user_name = payload.get("user_name")
    password = payload.get("password")
    if id is None or user_name is None or password is None:
        return "Unable to get params: Expected json with (id, user_name, password)", 406
    router_user: RouterUser = RouterUser.get_router_user_by_id(id)
    if router_user is None:
        return "Unable to get router_user_info", 500
    router_user.change_password(password)
    response = make_response("")
    return response, 200


# ---------------------------------Drop Router User  -------------------------------------

@app.route('/drop_router_user', methods=["POST"])
def drop_router_user():
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request):
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    id = payload.get("id")
    if id is None:
        return "Unable to get params: Expected json with (id)", 406
    router_user: RouterUser = RouterUser.get_router_user_by_id(id)
    if router_user is None:
        return "Unable to get router_user_info", 500
    router_user.drop_user_router(id)
    response = make_response("")
    return response, 200


# ----------------------------------MAIN ---------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
