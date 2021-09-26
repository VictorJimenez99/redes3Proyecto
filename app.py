from flask import Flask, render_template, make_response, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/set_cookie', methods=["POST"])
def set_cookie():  # put application's code here
    #return render_template("index.html")
    user = "Vic"
    if request.method == 'POST':
        user = request.form['nm']
    resp = make_response(render_template("main_page.html", user_name = user))
    resp.set_cookie('login', user)
    return resp

@app.route('/check_cookie')
def has_cookie():
    value = request.cookies.get('login')
    return f"login {value}"



if __name__ == '__main__':
    app.run(debug=True)
