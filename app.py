from time import time
from datetime import datetime

from flask import Flask, render_template, make_response, request, redirect, jsonify
from server.orm import db, SysUser, LoginCookie, RouterUser, Router, RouterConnectionTable, SysConfig, Log
from server.random import random_word, add_list, remove_list
from server.session import has_valid_session, get_cookie_from_session
from routers.router_conn import RouterConnection

app = Flask(__name__)

db_name = 'database.sqlite'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)

if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
    def _fk_pragma_on_connect(dbapi_con, con_record):  # noqa
        # print("turning on foreign keys for connection")
        dbapi_con.execute('pragma foreign_keys=ON')


    with app.app_context():
        from sqlalchemy import event

        event.listen(db.engine, 'connect', _fk_pragma_on_connect)
        # print("foreign keys are already on")


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
    user: SysUser = LoginCookie.get_owner(value)
    LoginCookie.logout_cookie(value)
    response.delete_cookie('access_key')
    # Log.new_event("Dropped Session", user.user_name)
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
    # Log.new_event("Created Login Token", user_name)

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

    value = request.cookies.get('access_key')
    user: SysUser = LoginCookie.get_owner(value)
    Log.new_event(f"Created new user: {user_name}", user.user_name)

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

    value = request.cookies.get('access_key')
    user_log: SysUser = LoginCookie.get_owner(value)
    # Log.new_event(f"Changed email for: {user.user_name}, new_val: {email} ", user_log.user_name)

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

    value = request.cookies.get('access_key')
    user_log: SysUser = LoginCookie.get_owner(value)
    Log.new_event(f"Changed password for: {user.user_name}", user_log.user_name)

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

    value = request.cookies.get('access_key')
    user_log: SysUser = LoginCookie.get_owner(value)
    Log.new_event(f"dropped sys_user with id: {id}", user_log.user_name)

    return response, 200


##################################################################################
#                               ROUTERS                                          #
#################################################################################

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
    response = make_response("")

    value = request.cookies.get('access_key')
    user_log: SysUser = LoginCookie.get_owner(value)
    Log.new_event(f"Configured rip protocol for router {router.name}", user_log.user_name)

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
    router.change_protocol("2")
    response = make_response("")

    value = request.cookies.get('access_key')
    user_log: SysUser = LoginCookie.get_owner(value)
    Log.new_event(f"Configured OSPF protocol for router: {router.name}", user_log.user_name)

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
    if router.protocol is not None:
        value = conn.no_ospf(router.protocol)
    value = conn.no_rip()
    router.change_protocol("3")
    response = make_response("")

    value = request.cookies.get('access_key')
    user_log: SysUser = LoginCookie.get_owner(value)
    Log.new_event(f"Configured OSPF protocol for router {router.name}", user_log.user_name)

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

    # proto_name = payload.get("proto_name")
    print(f"protocol: {protocol}")

    if name is None or ip_addr is None or protocol is None:
        return "Unable to get params: Expected json with (name, ip_addr, protocol)", 406
    possible_duplication = Router.get_router_by_name(name)
    if possible_duplication:
        return "Duplicated router; cannot add new router", 409
    Router.new_router(name, ip_addr, protocol)

    response = make_response("")

    value = request.cookies.get('access_key')
    user_log: SysUser = LoginCookie.get_owner(value)
    Log.new_event(f"Adding new router: {name}", user_log.user_name)

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

    value = request.cookies.get('access_key')
    user_log: SysUser = LoginCookie.get_owner(value)
    Log.new_event(f"Updating router with params: {name}, {ip_addr}, {protocol}", user_log.user_name)

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

    value = request.cookies.get('access_key')
    user_log: SysUser = LoginCookie.get_owner(value)
    Log.new_event(f"Dropping router: {router.name}", user_log.user_name)

    return response, 200


# ---------------------------------SetSNMP -------------------------------------
@app.route('/router/set_snmp', methods=["POST"])
def set_snmp():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request) and user.user_type != 1:
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    name = payload.get("router_name")
    key = payload.get("snmp_key")
    new_value = payload.get("snmp_new_value")
    if name is None or key is None or new_value is None:
        return "Unable to get params: Expected json with (router_name, snmp_key, snmp_new_value)", 406
    router: Router = Router.get_router_by_name(name)
    if router is None:
        return "Invalid router Name", 404
    valid_values = ["sys_name", "sys_contact", "sys_location"]

    if key not in valid_values:
        return "Invalid snmp_key (sys_name, sys_contact, sys_location)", 404

    if key == valid_values[0]:
        router.set_to_update_sys_name(new_value)
    elif key == valid_values[1]:
        router.set_to_update_sys_contact(new_value)
    else:
        router.set_to_update_sys_location(new_value)

    value = request.cookies.get('access_key')
    user_log: SysUser = LoginCookie.get_owner(value)
    Log.new_event(f"Marked: {router.name} for SNMP Update changed: {key} for: {new_value}", user_log.user_name)

    return f"Updated {key} for router: {router}", 200


# ---------------------------------GetSNMPInfo -------------------------------------
@app.route('/router/get_snmp', methods=["GET"])
def get_snmp_info():
    if request.method != 'GET':
        return "not a get method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request):
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    name = payload.get("router_name")

    if name is None:
        return "Unable to get Params: Expected JSON with (router_name)", 404

    if Router.get_router_by_name(name) is None:
        return "Unable to locate Router", 404

    return Router.get_snmp_values(name), 200


# ---------------------------------SetSNMPDropUpdate-------------------------------------
# Only for backend porpoises it updates the table while dropping the client update
# DO NOT TOUCH
# DO NOT TOUCH
# DO NOT TOUCH
# DO NOT TOUCH
@app.route('/router/set_snmp_drop_update', methods=["POST"])
def set_snmp_drop_update():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request) and user.user_type != 1:
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    name = payload.get("router_name")
    key = payload.get("snmp_key")
    new_value = payload.get("snmp_new_value")
    if name is None or key is None or new_value is None:
        return "Unable to get params: Expected json with (router_name, snmp_key, snmp_new_value)", 406
    router: Router = Router.get_router_by_name(name)
    if router is None:
        return "Invalid router Name", 404
    valid_values = ["sys_name", "sys_contact", "sys_location"]

    if key not in valid_values:
        return "Invalid snmp_key (sys_name, sys_contact, sys_location)", 404

    if key == valid_values[0]:
        setattr(router, valid_values[0], new_value)
        db.session.commit()
    elif key == valid_values[1]:
        setattr(router, valid_values[1], new_value)
        db.session.commit()
    else:
        setattr(router, valid_values[2], new_value)
        db.session.commit()

    setattr(router, "needs_snmp_read", False)
    setattr(router, "needs_snmp_update", False)
    db.session.commit()

    value = request.cookies.get('access_key')
    user_log: SysUser = LoginCookie.get_owner(value)
    Log.new_event(f"Updated SNMP {key} for new value: {new_value} at: {router.name}", user_log.user_name)

    return f"Updated {key} for router: {router} while drooping the update", 200


# ---------------------------------GetSNMPNeedsUpdate-------------------------------------
@app.route('/snmp/get_needs_update', methods=["GET"])
def get_snmp_needs_update():
    if request.method != 'GET':
        return "not a post method", 400
    if not has_valid_session(request):
        return "Unauthorized", 401
    li = Router.get_router_that_need_snmp_update()
    if li is None:
        return {"list": [],
                "sleep_time": SysConfig.get_value_of("snmp_client_update_await_time")}, 200
    real_list = []
    for router in li:
        ob = {"router_ip": router.ip_addr, "router_name": router.name}
        real_list.append(ob)

    object_to_return = {"list": real_list,
                        "sleep_time": SysConfig.get_value_of("snmp_client_update_await_time")}
    return object_to_return, 200


# ---------------------------------GetSNMPNeedsRead-------------------------------------
@app.route('/snmp/get_needs_read', methods=["GET"])
def get_snmp_needs_read():
    if request.method != 'GET':
        return "not a post method", 400
    if not has_valid_session(request):
        return "Unauthorized", 401
    li = Router.get_router_that_need_snmp_read()

    if li is None:
        return {"list": [],
                "sleep_time": SysConfig.get_value_of("snmp_client_read_await_time")}, 200

    real_list = []

    for router in li:
        ob = {"router_ip": router.ip_addr, "router_name": router.name}
        real_list.append(ob)

    object_to_return = {"list": real_list,
                        "sleep_time": SysConfig.get_value_of("snmp_client_read_await_time")}
    return object_to_return, 200


##################################################################################
#                               ROUTER_Connection                                #
##################################################################################

# -------------------------------DELETE Router Conn-----------------------------------
@app.route('/delete_router_conn', methods=['POST'])
def delete_router_conn():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request) and user.user_type != 1:
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    source = payload.get("source")
    dest = payload.get("destination")

    if source is None or dest is None:
        return "Unable to get params: Expected json with (source, destination)", 406
    router_source = Router.get_router_by_name(source)
    router_dest = Router.get_router_by_name(dest)
    if router_dest is None or router_source is None:
        return "Invalid Names: unregistered router", 404

    if not RouterConnectionTable.connection_exists(router_source, router_dest):
        return "A connection doesn't exist between those routers", 409

    RouterConnectionTable.drop_connection(router_source, router_dest)

    response = make_response("")
    return response, 200


##################################################################################
#                               TOPOLOGY                                         #
##################################################################################

@app.route('/update_topology', methods=['POST'])
def update_topology():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if user is None:
        return "Unauthorized", 401
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request) and user.user_type != 1:
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    routers: dict = payload.get("routers")
    connections: dict = payload.get("connections")

    if routers is None or connections is None:
        return "Unable to get params: Expected json with (routers(array), connections(array))", 406

    routers_in_db = list(map(lambda x: x.name, Router.get_router_all()))
    # print(routers_in_db)

    sent_routers: [] = []

    for rout in routers:
        rout_name = rout.get("name")
        rout_ip_addr = rout.get("ip_addr")
        rout_protocol = rout.get("protocol")
        if rout_name is None or rout_ip_addr is None or rout_protocol is None:
            return "Unable to get nested_params: Expected router json with (name, ip_addr, protocol)", 406

        it_exists: Router = Router.get_router_by_name(rout_name)
        if it_exists:
            # print(f"saved from oblivion: {it_exists}")
            sent_routers.append(it_exists.name)
            continue

        n_router = Router(name=rout_name, ip_addr=rout_ip_addr, protocol=rout_protocol)
        db.session.add(n_router)
        sent_routers.append(rout_name)

    # print(f"sent: {sent_routers}, in_db: {routers_in_db}")

    routers_to_be_added = add_list(routers_in_db, sent_routers)
    routers_to_be_removed = remove_list(routers_in_db, sent_routers)

    if len(routers_to_be_added) != 0:
        log_cookie_owner = request.cookies.get('access_key')
        user_log: SysUser = LoginCookie.get_owner(log_cookie_owner)
        Log.new_event(f"Adding routers: {routers_to_be_added}", user_log.user_name)
    if len(routers_to_be_removed) != 0:
        log_cookie_owner = request.cookies.get('access_key')
        user_log: SysUser = LoginCookie.get_owner(log_cookie_owner)
        Log.new_event(f"Removing routers: {routers_to_be_removed}", user_log.user_name)

    # print(f"add: {routers_to_be_added}, delete: {routers_to_be_removed}")

    for add_r in routers_to_be_added:
        active: Router = Router.get_router_by_name(add_r)
        setattr(active, "needs_snmp_read", True)
        # print(f"adding: {add_r}")
        db.session.add(active)
        db.session.commit()
    for rem_r in routers_to_be_removed:
        active = Router.get_router_by_name(rem_r)
        # print(f"removing: {rem_r}")
        db.session.delete(active)
        db.session.commit()

    for con in connections:
        router_source = Router.get_router_by_name(con.get("source"))
        router_destination = Router.get_router_by_name(con.get("destination"))
        router_source_interface = con.get("source_interface")
        router_destination_interface = con.get("destination_interface")

        if router_source is None or router_destination is None or router_destination_interface is None or router_source_interface is None:
            return "Unable to create connection", 409

        if RouterConnectionTable.connection_exists(router_source, router_destination):
            possible_update: RouterConnectionTable = RouterConnectionTable.get_connection(router_source,
                                                                                          router_destination)
            # print(f"Saved connection from oblivion: {possible_update}")
            if possible_update.source_interface != router_source_interface or possible_update.destination_interface != router_destination_interface:
                possible_update.update_interfaces(router_source_interface, router_destination_interface)
                # print(f"But updated interface: {possible_update}")
            continue

        connection = RouterConnectionTable(source=router_source.id,
                                           destination=router_destination.id,
                                           source_interface=router_source_interface,
                                           destination_interface=router_destination_interface)
        db.session.add(connection)

    db.session.commit()

    await_time = int(SysConfig.get_value_of("topology_test_await_time"))

    json_resp = {"message": "Success updating table", "await_time": await_time}

    return json_resp, 200


# --------------------------------- Json Network  -------------------------------------
@app.route('/get_topology', methods=['POST'])
def get_topology():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request) and user.user_type != 1:
        return "Unauthorized", 401

    routersConnections = RouterConnectionTable.get_all()
    edges = []
    convi = []
    for con in routersConnections:

        routerSource = Router.get_router_by_id(con.source)
        routerDestination = Router.get_router_by_id(con.destination)
        if (
                f'{routerSource.name}-{routerDestination.name}' not in convi and f'{routerDestination.name}-{routerSource.name}' not in convi):
            dic = {'data': {'id': f'{routerSource.name}-{routerDestination.name}', 'source': routerSource.name,
                            'target': routerDestination.name,
                            'label': f'{con.source_interface}-{con.destination_interface}', }}
            edges.append(dic)
            convi.append(f'{routerSource.name}-{routerDestination.name}')
    routers = Router.get_router_all()
    nodes = []
    for router in routers:
        dic = {'data': {'id': router.name}}
        nodes.append(dic)
    topologyDic = {
        'nodes': nodes,
        'edges': edges
    }
    return topologyDic, 200


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
    new_router: RouterUser = RouterUser.get_router_user_by_name(name)

    for router in routers:
        conn = RouterConnection(router.ip_addr, access_user, access_password)
        value = conn.add_router_user(new_router, password)

    response = make_response("")

    value = request.cookies.get('access_key')
    user_log: SysUser = LoginCookie.get_owner(value)
    Log.new_event(f"Adding new router user: {new_router.user_name}", user_log.user_name)

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
    router_user.change_password(password)
    router_user.change_user_type(user_type)
    for router in routers:
        conn = RouterConnection(router.ip_addr, access_user, access_password)
        value = conn.update_router_user(router_user, password)
    response = make_response("")

    value = request.cookies.get('access_key')
    user_log: SysUser = LoginCookie.get_owner(value)
    Log.new_event(f"Updating router user: {user_name}. {password}, {user_type}", user_log.user_name)

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

    value = request.cookies.get('access_key')
    user_log: SysUser = LoginCookie.get_owner(value)
    Log.new_event(f"Dropping Router User: {router_user.user_name}", user_log.user_name)

    return response, 200


##################################################################################
#                               SysConfig                                        #
##################################################################################

# ---------------------------------View SysConfig  -------------------------------

@app.route('/sys_config_view')
def sys_config_view():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if has_valid_session(request) and user.user_type == 1:
        configs = SysConfig.get_all()
        return render_template("otros/configuracion_general.html", configs=configs, len=len(configs),
                               user_type=user.user_type)
    else:
        return redirect("/")


# --------------------------------- SysConfig list  -------------------------------

@app.route("/sys_config_get_all", methods=['POST', 'GET'])
def sys_config_get_all():
    if request.method != 'POST' and request.method != 'GET':
        return "not a valid method", 400
    if not has_valid_session(request):
        return "Unauthorized", 401
    list_of_val = {"values": SysConfig.get_all_json()}
    return list_of_val, 200


@app.route("/sys_config_update", methods=['POST'])
def sys_config_update():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request) and user.user_type != 1:
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    key = payload.get("key")
    new_value = payload.get("new_value")
    if key is None or new_value is None:
        return "Unable to get params: Expected json with (key, new_value)", 406

    if SysConfig.key_exists(key):
        SysConfig.update_value(key, new_value)

        value = request.cookies.get('access_key')
        user_log: SysUser = LoginCookie.get_owner(value)
        Log.new_event(f"Successfully updated SysConfig: {key}, with {new_value}", user_log.user_name)

        return f"Successfully updated {key}", 200
    return f"Unable to locate {key}", 404


##################################################################################
#                               LOG                                              #
##################################################################################

# ---------------------------------View log-------------------------------

@app.route('/log_view')
def log_view():
    user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
    if has_valid_session(request):
        logs = Log.get_all()
        for log in logs:
            log.time = datetime.utcfromtimestamp(log.time).strftime('%Y-%m-%d %H:%M:%S')
        return render_template("otros/log_info.html", logs=logs, len=len(logs),
                               user_type=user.user_type)
    else:
        return redirect("/")


# ---------------------------------GET ALL-------------------------------

@app.route("/log_get_all", methods=['POST', 'GET'])
def log_get_all():
    if request.method != 'POST' and request.method != 'GET':
        return "not a valid method", 400
    if not has_valid_session(request):
        return "Unauthorized", 401
    list_of_val = {"values": Log.get_all_json()}
    return list_of_val, 200


# ---------------------------------GET NOT SENT-------------------------------
@app.route("/log_get_not_sent", methods=['POST', 'GET'])
def leg_get_not_sent():
    if request.method != 'POST' and request.method != 'GET':
        return "not a valid method", 400
    if not has_valid_session(request):
        return "Unauthorized", 401
    list_of_val = {"values": Log.get_not_sent_json(),
                   "sleep_time": SysConfig.get_value_of("smtp_client_await_time_mail")}
    return list_of_val, 200


@app.route("/log/set_sent_status", methods=['POST'])
def set_sent():
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
    Log.change_sent_status(id, True)
    return "Notified", 200


@app.route("/log_get_mails", methods=['POST', 'GET'])
def leg_get_emails():
    if request.method != 'POST' and request.method != 'GET':
        return "not a valid method", 400
    if not has_valid_session(request):
        return "Unauthorized", 401
    list_of_val = {"emails": SysUser.get_all_emails()}
    return list_of_val, 200


##################################################################################
#                               SNMP PACKETS                                         #
##################################################################################

# --------------------------------- Json list snmp request  -------------------------------------
@app.route('/get_json_list_snmp_pack', methods=['POST', 'GET'])
def get_json_list_snmp_pack():
    if not has_valid_session(request):
        return "Unauthorized", 401
    routersConnections = RouterConnectionTable.get_all()
    list = []
    for con in routersConnections:
        routerSource: Router = Router.get_router_by_id(con.source)
        dic = {'name': routerSource.name, 'ip_addr': routerSource.ip_addr, 'interface': con.source_interface}
        list.append(dic)
    sys_config: SysConfig = SysConfig.get_value_of("snmp_packets_await_time")
    time = 10
    if sys_config is not None:
        time = int(sys_config)
    response = {
        'list': list,
        'sleep': time
    }
    return response, 200

# --------------------------------- Json sent, receive packets  -------------------------------------
@app.route('/get_sent_received_packets', methods=['POST'])
def get_sent_received_packets():
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request):
        return "Unauthorized", 401
    payload: dict = request.get_json(force=True)
    name = payload.get("name")
    interface = payload.get("interface")
    if name is None or interface is None:
        return "Unable to get params: Expected json with (name, interface)", 406
    router: Router = Router.get_router_by_name(name)
    routersConnections: RouterConnectionTable = RouterConnectionTable.get_connection_r_i(router, interface)
    list = {'sent': routersConnections.sent, 'received': routersConnections.received}
    return list, 200


# --------------------------------- Update packets info  -------------------------------------
@app.route('/update_snmp_pack', methods=['POST'])
def update_snmp_pack():
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request):
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    name = payload.get("name")
    interface = payload.get("interface")
    sent = payload.get("sent")
    received = payload.get("received")
    if interface is None or name is None or sent is None or received is None:
        return "Unable to get params: Expected json with (name, interface, sent, received)", 406
    router: Router = Router.get_router_by_name(name)
    routerConnection: RouterConnectionTable = RouterConnectionTable.get_connection_r_i(router, interface)
    routerConnection.update_sent(sent)
    routerConnection.update_received(received)
    response = make_response("")

    value = request.cookies.get('access_key')
    user_log: SysUser = LoginCookie.get_owner(value)
    Log.new_event(f"Updating snmp router packets: {name}, {interface}, enviados {sent}, recibidos {received}", user_log.user_name)

    return response, 200


##################################################################################
#                               GRAFICAS                                         #
##################################################################################

# ---------------------------------View Graficas  -------------------------------------
@app.route('/charts_view')
def charts_view():
    if has_valid_session(request):
        user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
        users = SysUser.get_all_users()
        routers = Router.get_router_all()
        router_users = RouterUser.get_all_users()
        return render_template("otros/charts.html", len_users=len(users), users=users, len_routers=len(routers),
                               routers=routers, len_router_users=len(router_users), router_users=router_users,
                               user_type=user.user_type)
    else:
        return redirect("/")

@app.route('/search_router_con', methods=['POST'])
def search_router_con():
    if request.method != 'POST':
        return "not a post method", 400
    if not request.is_json:
        return "not json", 415
    if not has_valid_session(request):
        return "Unauthorized", 401

    payload: dict = request.get_json(force=True)
    name = payload.get("name")
    if name is None:
        return "Unable to get params: Expected json with (name)", 406
    router: Router = Router.get_router_by_name(name)
    routerConnectionTable: RouterConnectionTable = RouterConnectionTable.get_connections_r_s(router)
    list = []
    for routerConnection in routerConnectionTable:
        info = { 'interface':routerConnection.source_interface }
        list.append(info)
    dir = {
        'conns': list
    }
    return dir, 200



# ---------------------------------View Graficas SNMP  -------------------------------------
@app.route('/charts_view_snmp')
def charts_view_snmp():
    if has_valid_session(request):
        user: SysUser = LoginCookie.get_owner(get_cookie_from_session(request))
        users = SysUser.get_all_users()
        routers = Router.get_router_all()
        router_users = RouterUser.get_all_users()
        return render_template("otros/chart_snmp.html", len_users=len(users), users=users, len_routers=len(routers),
                               routers=routers, len_router_users=len(router_users), router_users=router_users,
                               user_type=user.user_type, search_router_con= search_router_con)
    else:
        return redirect("/")






# ----------------------------------MAIN -----------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
