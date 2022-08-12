from flask import Flask, render_template, request, redirect, jsonify, session
from src.database import HotelDatabase, UserDatabase

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = b'8fc4e6768109ca56d4314b2f540ac0fafabaa1d9019252d472888856707a218e'
userDB = UserDatabase()
hotelDB = HotelDatabase()

@app.route('/')
def index():
    return redirect('/welcome')

@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    message = None
    if 'username' in session:
        message = session['username']
    return render_template('welcome.html', message=message)

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
                session['username'] = userInfo
            else:
                message = 'User is NOT in database.'
    return render_template('login.html', message=message)

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
                render_template('register.html', message=message)
    return render_template('register.html', message=message)

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect('/')

@app.route('/api/reserved')
def reservedRoom():
    username = str(request.args.get('username')).strip()
    return jsonify(userDB.getReservedRooms(username))

if (__name__ == "__main__"):
    app.run(host='127.0.0.1', port=8080, debug=True)