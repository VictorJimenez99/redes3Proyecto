from flask import Flask, render_template, make_response, request
from server.orm import db, SysUser
from flask_sqlalchemy import SQLAlchemy

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


@app.route('/set_cookie', methods=["POST"])
def set_cookie():
    # put application's code here
    # return render_template("index.html")
    user = "Vic"
    if request.method == 'POST':
        user = request.form['nm']
    resp = make_response(render_template("main_page.html", user_name=user))
    resp.set_cookie('login', user)
    return resp


@app.route('/check_cookie')
def has_cookie():
    value = request.cookies.get('login')
    return f"login {value}"


@app.route('/test_db')
def test_db():
    try:
        test = SysUser.validate_credentials("root", "root")
        print(test)
        return f'<h1> It works {str(test)} </h1>'
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text


if __name__ == '__main__':
    app.run(debug=True)
