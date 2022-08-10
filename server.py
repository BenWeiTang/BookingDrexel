from flask import Flask, render_template, request, redirect, jsonify
from src.database import HotelDatabase, UserDatabase

app = Flask(__name__, static_folder='static', static_url_path='')
userDB = UserDatabase()
hotelDB = HotelDatabase()

@app.route('/')
def index():
    return '<h1>HOME</h>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = str(request.form['username']).strip()
        typedPassword = str(request.form['password']).strip()
        if username and typedPassword:
            userInfo = userDB.getUserInfo(username)
            if userInfo is not None and typedPassword == userInfo['password']:
                message = 'User IS in database.'
            else:
                message = 'User is NOT in database.'
    return render_template('test-login.html', message=message)

@app.route('/register', methods=['GET', 'POST'])
def create():
    message = None
    if request.method == 'POST':
        username = str(request.form['username']).strip()
        password = str(request.form['password']).strip()
        if username and password:
            success = userDB.addUser(username, password)
            if success:
                return redirect('/login')
            else:
                message = 'User already exists.'
                render_template('test-register.html', message=message)
    return render_template('test-register.html', message=message)

@app.route('/api/reserved')
def reservedRoom():
    username = str(request.args.get('username')).strip()
    return jsonify(userDB.getReservedRooms(username))

if (__name__ == "__main__"):
    app.run(host='127.0.0.1', port=8080, debug=True)