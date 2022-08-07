from flask import Flask, render_template
from database import Database

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/')
def index():
    return '<h1>HOME</h>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('test-login.html')

@app.route('/register', methods=['GET', 'POST'])
def create():
    return render_template('test-register.html')

# Put last
if (__name__ == "__main__"):
    app.run(host='127.0.0.1', port=8080, debug=True)