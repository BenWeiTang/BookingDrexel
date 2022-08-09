import sqlite3

class Database:
    def __init__(self):
        # Be careful with this
        self.conn = sqlite3.connect('BookingDrexel.db', check_same_thread=False)
        # self.conn = sqlite3.connect(':memory:')
    
    def execute(self, sql: str, parameters: tuple):
        result = None
        with self.conn:
            c = self.conn.cursor()
            c.execute(sql, parameters)
            result = c.fetchall()
        return result
    
    def __del__(self):
        self.conn.close()
  
class UserDataBase(Database):
    def __init__(self) -> None:
        super().__init__()
        self.execute("""CREATE TABLE IF NOT EXISTS users (
            username TEXT NOT NULL, 
            password TEXT NOT NULL)""", tuple())
        
    def hasUser(self, username: str) -> bool:
        instanceNum = len(self.execute("SELECT * FROM users WHERE username=?", (username,)))
        return instanceNum != 0
    
    def addUser(self, username: str, password: str) -> bool:
        if self.hasUser(username):
            print("User {} already exists.".format(username))
            return False 
        self.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        return True

    def getUserInfo(self, username: str) -> dict:
        if not self.hasUser(username):
            print("User {} does not exist.".format(username))
            return None 
        data = self.execute("SELECT * FROM users WHERE username=?", (username,))[0]
        return {'username': data[0], 'password': data[1]}

    # Only works on file not RAM db
    def getReservedRooms(self, username: str) -> list:
        info = self.getUserInfo(username)
        rooms = self.execute("SELECT * FROM rooms WHERE reservedBy=?", (info['username'],))
        result = list()
        for room in rooms:
            result.append({'hotel': room[0], 'rating': room[1], 'roomNum': room[2], 'reservedBy': room[3]})
        return result

class HotelDatabase(Database):
    def __init__(self) -> None:
        super().__init__()
        self.execute("""CREATE TABLE IF NOT EXISTS rooms (
            hotel TEXT NOT NULL, 
            rating REAL NOT NULL,
            location TEXT NOT NULL,
            roomCount INTEGER NOT NULL)""", tuple())
    
    def hasHotel(self, hotel: str):
        instanceNum = len(self.execute("SELECT * FROM rooms WHERE hotel=?", (hotel,)))
        return instanceNum != 0

    def addHotel(self, hotel: str, rating: float, location: str, roomCount: int) -> bool:
        if self.hasHotel(hotel):
            print("Hotel {} already exists.".format(hotel))
            return False
        self.execute("INSERT INTO rooms VALUES (?, ?, ?, ?)", (hotel, rating, location, roomCount))
        return True

# Need testing
class ReservationDatabase(Database):
    def __init__(self) -> None:
        super().__init__()
        self.execute("""CREATE TABLE IF NOT EXISTS reservations (
            hotel TEXT NOT NULL,
            reservedBy TEXT NOT NULL,
            fromDate TEXT NOT NULL,
            toDate TEXT NOT NULL)""", tuple())
    
    def hasRoom(self, db: HotelDatabase, hotel: str, fromDate: str, toDate: str) -> bool:
        pass

    def bookRoom(self, hotel: str, fromDate: str, toDate: str) -> bool:
        pass

    def getEmptyRoomCount(self, hotel: str) -> int:
        pass