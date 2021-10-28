from time import time

from flask import Flask, render_template, make_response, request, redirect, jsonify
from server.orm import db, SysUser, LoginCookie, RouterUser, Router
from server.random import random_word
from server.session import has_valid_session, get_cookie_from_session
from routers.router_conn import RouterConnection

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
        user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
        return render_template("logged_index.html", user_type=user.user_type)
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
        user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
        return render_template("user/app_user_pass.html", user_type=user.user_type)
    else:
        return redirect("/")


# -----------------------------View SysUser update -------------------------------------------
@app.route('/app_user_list')
def app_user_list():
    if has_valid_session(request):
        users = SysUser.get_all_users()
        user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
        return render_template("user/app_user_list.html", len=len(users), users=users, user_type=user.user_type)
    else:
        return redirect("/")


# -----------------------------View SysUser add -------------------------------------------
@app.route('/add_view_sys_user')
def add_view_sys_user():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if has_valid_session(request) and user.user_type == 1:
        return render_template("user/add_view_sys_user.html", user_type=user.user_type)
    else:
        return redirect("/")


# ----------------------------ADD_SYS_USER----------------------------------------
@app.route('/add_sys_user', methods=["POST"])
def add_sys_user():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request) and user.user_type != 1:
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    user_name = payload.get("new_name")
    password = payload.get("new_password")
    user_type = payload.get("user_type")
    if user_name is None or password is None or user_type is None:
        return "Unable to get params: Expected json with (new_name, new_password, user_type)", 406
    possible_duplication = SysUser.get_user_by_name(user_name)
    if possible_duplication:
        return "Duplicated user; cannot add new user", 409

    SysUser.add_new_sys_user(user_name, password, user_type)

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


# ---------------------------------Drop SysUser  -------------------------------------

@app.route('/drop_SysUser', methods=["POST"])
def drop_SysUser():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request) and user.user_type != 1:
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    id = payload.get("id")
    if id is None:
        return "Unable to get params: Expected json with (id)", 406
    sysUser: SysUser = SysUser.get_user_by_id(id)
    if sysUser is None:
        return "Unable to get router_user_info", 500
    sysUser.drop_user(id)
    response = make_response("")
    return response, 200


##################################################################################
#                               ROUTERS                                          #
##################################################################################

# -------------------------------View Router List -----------------------------------

@app.route('/router_list')
def router_list():
    if has_valid_session(request):
        routers = Router.get_router_all()
        user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
        return render_template("router/router_list.html", len=len(routers), users=routers, user_type=user.user_type)
    else:
        return redirect("/")


# -------------------------------View Add Router  -----------------------------------

@app.route('/add_view_router')
def add_view_router():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if has_valid_session(request) and user.user_type == 1:
        return render_template("router/add_view_router.html", user_type=user.user_type)
    else:
        return redirect("/")


# -------------------------------View Configure Router Protocol  -----------------------------------

@app.route('/router_configure_protocol')
def router_configure_protocol():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if has_valid_session(request) and user.user_type == 1:
        routers = Router.get_router_all()
        users = RouterUser.get_all_users()
        return render_template("router/router_configure_protocol.html", len_routers=len(routers), routers=routers,
                               len_users=len(users), users=users, user_type=user.user_type, router=None)
    else:
        return redirect("/")


@app.route('/router_configure_protocol/<int:id>')
def router_configure_protocol_par(id: int):
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if has_valid_session(request) and user.user_type == 1:
        router: Router = Router.get_router_by_id(id)
        routers = Router.get_router_all()
        users = RouterUser.get_all_users()
        return render_template("router/router_configure_protocol.html", len_routers=len(routers), routers=routers,
                               len_users=len(users), users=users, user_type=user.user_type, router=router)
    else:
        return redirect("/")


# --------------------------------- router RIP_V2  -------------------------------------

@app.route('/router/<string:router_ip>/router_rip', methods=["POST"])
def add_router_rip(router_ip: str):
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request) and user.user_type != 1:
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    networks = payload.get("networks")
    ip_addr = router_ip
    router_user = payload.get("router_user")
    router_user_password = payload.get("router_user_password")
    if networks is None or ip_addr is None or router_user is None or router_user_password is None:
        return "Unable to get params: Expected json with (networks, router_user, router_user_password)", 406

    conn = RouterConnection(ip_addr, router_user, router_user_password)
    value = conn.configure_rip_protocol(networks)
    router: Router = Router.get_router_by_ip(ip_addr)
    print("protocolo:" + router.protocol)
    if router.protocol_name is not None:
        print("entre")
        value = conn.no_eigrp(router.protocol_name)
        value = conn.no_ospf(router.protocol_name)
    router.change_protocol("1")
    response = make_response(value)
    return response, 200


# --------------------------------- router OSPF  -------------------------------------

@app.route('/router/<string:router_ip>/router_ospf', methods=["POST"])
def add_router_ospf(router_ip: str):
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request) and user.user_type != 1:
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    networks = payload.get("networks")
    ip_addr = router_ip
    router_user = payload.get("router_user")
    proto_name = payload.get("proto_name")
    router_user_password = payload.get("router_user_password")
    if networks is None or ip_addr is None or router_user is None or router_user_password is None or proto_name is None:
        return "Unable to get params: Expected json with (networks, router_user, router_user_password,proto_name)", 406

    conn = RouterConnection(ip_addr, router_user, router_user_password)
    value = conn.configure_ospf_protocol(networks, proto_name)
    router: Router = Router.get_router_by_ip(ip_addr)
    if router.protocol_name is not None:
        value = conn.no_eigrp(router.protocol_name)
    value = conn.no_rip()
    router.change_protocol("2", proto_name)
    response = make_response(value)
    return response, 200


# --------------------------------- router EIGRP  -------------------------------------

@app.route('/router/<string:router_ip>/router_eigrp', methods=["POST"])
def add_router_eigrp(router_ip: str):
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request) and user.user_type != 1:
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    networks = payload.get("networks")
    proto_name = payload.get("proto_name")
    ip_addr = router_ip
    router_user = payload.get("router_user")
    router_user_password = payload.get("router_user_password")
    if networks is None or ip_addr is None or router_user is None or router_user_password is None or proto_name is None:
        return "Unable to get params: Expected json with (networks, router_user, router_user_password,proto_name)", 406

    conn = RouterConnection(ip_addr, router_user, router_user_password)
    value = conn.configure_eigrp_protocol(networks, proto_name)
    router: Router = Router.get_router_by_ip(ip_addr)
    if router.protocol_name is not None:
        value = conn.no_ospf(router.protocol_name)
    value = conn.no_rip()
    router.change_protocol("2", proto_name)
    response = make_response(value)
    return response, 200


# ---------------------------------add Router  -------------------------------------

@app.route('/add_router', methods=["POST"])
def add_router():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request) and user.user_type != 1:
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
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request) and user.user_type != 1:
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


# ---------------------------------Drop Router  -------------------------------------

@app.route('/drop_router', methods=["POST"])
def drop_router():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request) and user.user_type != 1:
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
        user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
        users = RouterUser.get_all_users()
        return render_template("user_router/router_user_list.html", len=len(users), users=users,
                               user_type=user.user_type)
    else:
        return redirect("/")


# -----------------------------View Router User add -------------------------------------------
@app.route('/add_view_router_user')
def add_view_router_user():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if has_valid_session(request) and user.user_type == 1:
        users: RouterUser = RouterUser.get_all_users()
        return render_template("user_router/add_view_router_user.html", user_type=user.user_type, len=len(users),
                               users=users)
    else:
        return redirect("/")


# -----------------------------View Router User update -------------------------------------------
@app.route('/update_view_router_user/<int:router_user_id>', methods=["GET"])
def update_view_router_user(router_user_id: int):
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    router_user: RouterUser = RouterUser.get_router_user_by_id(router_user_id)
    if has_valid_session(request) and user.user_type == 1:
        users: RouterUser = RouterUser.get_all_users()
        return render_template("user_router/update_view_router_user.html", router_user=router_user,
                               user_type=user.user_type, len=len(users), users=users)
    else:
        return redirect("/")


# ---------------------------------Add Router User  -------------------------------------

@app.route('/add_router_user', methods=["POST"])
def add_router_user():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request) and user.user_type != 0:
        print(get_cookie_from_session(request))
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    name = payload.get("user_name")
    password = payload.get("password")
    user_type = payload.get("user_type")
    access_user = payload.get("access_user")
    access_password = payload.get("access_password")
    if name is None or name is None or password is None or user_type is None or access_user is None or access_password is None:
        return "Unable to get params: Expected json with (user_name, password, user_type)", 406
    possible_duplication = RouterUser.get_router_user_by_name(name)
    if possible_duplication:
        return "Duplicated router user; cannot add new user router", 409
    if not RouterUser.validate_credentials(access_user, access_password):
        return "Invalid_Credentials", 409
    routers = Router.get_router_all()
    if not len(routers) > 0:
        return "Se necesita dar de alta al menor un router", 409
    RouterUser.new_user_router(name, password, user_type)
    new_router: RouterUser = RouterUser.get_router_user_by_name(name);

    for router in routers:
        conn = RouterConnection(router.ip_addr, access_user, access_password)
        value = conn.add_router_user(new_router, password)

    response = make_response("")
    return response, 200


# ---------------------------------Update Router User  -------------------------------------

@app.route('/update_router_user', methods=["POST"])
def update_router_user():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request) and user.user_type != 1:
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    id = payload.get("id")
    user_name = payload.get("user_name")
    password = payload.get("password")
    user_type = payload.get("user_type")
    access_user = payload.get("access_user")
    access_password = payload.get("access_password")
    if id is None or user_name is None or password is None or user_type is None:
        return "Unable to get params: Expected json with (id, user_name, password, user_type)", 406
    router_user: RouterUser = RouterUser.get_router_user_by_id(id)
    if router_user is None:
        return "Unable to get router_user_info", 500
    routers = Router.get_router_all()
    if not len(routers) > 0:
        return "Se necesita dar de alta al menor un router", 409
    RouterUser.new_user_router(user_name, password, user_type)
    new_router: RouterUser = RouterUser.get_router_user_by_name(user_name)
    for router in routers:
        conn = RouterConnection(router.ip_addr, access_user, access_password)
        value = conn.update_router_user(new_router, password)
    router_user.change_password(password)
    router_user.change_user_type(user_type)
    response = make_response("")
    return response, 200


# ---------------------------------Drop Router User  -------------------------------------

@app.route('/drop_router_user', methods=["POST"])
def drop_router_user():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request) and user.user_type != 1:
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    id = payload.get("id")
    access_user = payload.get("access_user")
    access_password = payload.get("access_password")
    if id is None or access_user is None or access_password is None:
        return "Unable to get params: Expected json with (id, access_user, access_password)", 406
    router_user: RouterUser = RouterUser.get_router_user_by_id(id)
    if router_user is None:
        return "Unable to get router_user_info", 500
    routers = Router.get_router_all()
    if not len(routers) > 0:
        return "Se necesita dar de alta al menor un router", 409
    for router in routers:
        conn = RouterConnection(router.ip_addr, access_user, access_password)
        value = conn.drop_router_user(router_user)

    router_user.drop_user_router(id)
    response = make_response("")
    return response, 200


# ----------------------------------MAIN ---------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
