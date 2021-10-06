from flask import Flask, render_template, make_response, request
from server.orm import db, SysUser, LoginCookie

app = Flask(__name__)

db_name = 'database.sqlite'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)




@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/create_session', methods=["POST"])
def set_cookie():
    if request.method != 'POST':
        return "not a post method"
    if not request.is_json:
        return "not json"
    payload: dict = request.get_json(force=True)
    user_name = payload.get("name")
    password = payload.get("password")
    if SysUser.validate_credentials(user_name, password):
        user = SysUser.get_user_by_name(user_name)
        LoginCookie.new_cookie("value:1", user)


    return "Ok"


@app.route('/check_cookie')
def has_cookie():
    value = request.cookies.get('login')
    return f"login {value}"


@app.route('/test_db')
def test_db():
    try:
        test = SysUser.validate_credentials("root", "root")
        #print(test)
        return f'<h1> It works {str(test)} </h1>'
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text


if __name__ == '__main__':
    app.run(debug=True)
