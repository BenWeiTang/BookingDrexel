import json
from flask import Flask, render_template, request, redirect, jsonify, session
from src.database import HotelDatabase, ReservationDatabase, UserDatabase, WishlistDatabase

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = b'8fc4e6768109ca56d4314b2f540ac0fafabaa1d9019252d472888856707a218e'
userDB = UserDatabase()
hotelDB = HotelDatabase()
reservationDB = ReservationDatabase()
wishlistDB = WishlistDatabase()
hotelDB.addDefaultHotels()

@app.route('/')
def index():
    return redirect('/welcome')

@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    if request.method == 'POST':
        # These input fields must be required on the html side
        # Even if user isn't loggded in, the chosen hotel and from-to dates should be stored in session
        session['hotel'] = request.form['hotel']
        session['fromDate'] = request.form['fromDate']
        session['toDate'] = request.form['toDate']
        return redirect('/search')
    else:
        username = session['username'] if 'username' in session else None
        hotel = session['hotel'] if 'hotel' in session else None
        fromDate = session['fromDate'] if 'fromDate' in session else None
        toDate = session['toDate'] if 'toDate' in session else None
        allHotels = hotelDB.getAllHotelNames()
        return render_template('welcome.html', allHotels= allHotels, username=username, hotel=hotel, fromDate=fromDate, toDate=toDate)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = str(request.form['username']).strip()
        typedPassword = str(request.form['password']).strip()
        if username and typedPassword:
            userInfo = userDB.getUserInfo(username)
            if userInfo is not None and typedPassword == userInfo['password']:
                session['username'] = userInfo['username']
                return redirect('/welcome')
            else:
                message = 'Username or password incorrect.'
    return render_template('login.html', message=message)

@app.route('/register', methods=['GET', 'POST'])
def register():
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

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        hotel = session['hotel'] if session['hotel'] != "0" else None
        fromDate = hotelDB.dateStrToTup(session['fromDate'])
        toDate = hotelDB.dateStrToTup(session['toDate'])
        allAvailHotels = json.dumps(hotelDB.getAvailableHotelsFromTo(hotel, fromDate, toDate))
        return render_template('search.html', allAvailHotels=allAvailHotels)
    else:
        hotel = request.form['hotel']
        username = request.form['username']
        fromStr = request.form['fromDate']
        toStr = request.form['toDate']
        toAdd = request.form['toAdd'] == "true"
        fromDate = wishlistDB.dateStrToTup(fromStr)
        toDate = wishlistDB.dateStrToTup(toStr)
        if toAdd:
            wishlistDB.addWishlist(username, hotel, fromDate, toDate)
        else:
            wishlistDB.removeWishlist(username, hotel, fromDate, toDate)
        return redirect('/search')

@app.route('/wishlist', methods=['GET', 'POST'])
def wishlist():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        username = request.form['username']
        hotel = request.form['hotel']
        fromStr = request.form['fromDate']
        toStr = request.form['toDate']
        fromDate = wishlistDB.dateStrToTup(fromStr)
        toDate = wishlistDB.dateStrToTup(toStr)
        wishlistDB.removeWishlist(username, hotel, fromDate, toDate)
    return render_template('wishlist.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
        session.pop('hotel', None)
        session.pop('fromDate', None)
        session.pop('toDate', None)
    return redirect('/')

@app.route('/api/reserved')
def reservedRoom():
    username = str(request.args.get('username')).strip()
    return jsonify(userDB.getReservedRooms(username))

@app.route('/api/available')
def availableRoom():
    hotel = request.args.get('hotel')
    hotel = hotel if hotel != "0" else None
    fromDate = hotelDB.dateStrToTup(str(request.args.get('fromDate')))
    toDate = hotelDB.dateStrToTup(str(request.args.get('toDate')))
    result = hotelDB.getAvailableHotelsFromTo(hotel, fromDate, toDate)
    if not 'username' in session:
        for r in result:
            r['canWishlist'] = "False"
    else:
        for r in result:
            if not wishlistDB.hasWishlist(session['username'], r['hotel'], fromDate, toDate):
                r['canWishlist'] = "True"
            else:
                r['canWishlist'] = "False" 
    return jsonify(result)

@app.route('/api/wishlist')
def getUserWishilist():
    username = request.args.get('username')
    wishlists = wishlistDB.getWishList(username)
    return jsonify(wishlists)

if (__name__ == "__main__"):
    app.run(host='127.0.0.1', port=8080, debug=True)