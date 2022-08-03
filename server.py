from flask import Flask

app = Flask(__name__, static_folder='static', static_url_path='')

if (__name__ == "__main__"):
    app.run(host='127.0.0.1', port=8080, debug=True)