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
            roomNum INTEGER NOT NULL,
            reservedBy TEXT NOT NULL)""", tuple())
    
    def hasRoom(self, hotel: str, roomNum: int) -> None:
        instanceNum = len(self.execute("SELECT * FROM rooms WHERE hotel=? AND roomNum=?", (hotel, roomNum)))
        return instanceNum != 0
    
    def isRoomTaken(self, hotel: str, roomNum: int) -> bool:
        if not self.hasRoom(hotel, roomNum):
            print("Hotel room {} {} does not exist.".format(hotel, roomNum))
            return
        taken = self.execute("SELECT reservedBy FROM rooms WHERE hotel=? AND roomNum=?", (hotel, roomNum))
        return taken[0][0] != ''

    def addRoom(self, hotel: str, rating: float, roomNum: int) -> bool:
        if self.hasRoom(hotel, roomNum):
            print("Hotel room {} {} already exist.".format(hotel, roomNum))
            return False
        self.execute("INSERT INTO rooms VALUES (?, ?, ?, ?)", (hotel, rating, roomNum, ''))
        return True
    
    def bookRoom(self, hotel: str, roomNum: int, username: str) -> bool:
        if not self.hasRoom(hotel, roomNum):
            print("Hotel room {} {} does not exist.".format(hotel, roomNum))
            return False
        self.execute("UPDATE rooms SET reservedBy=? WHERE hotel=? AND roomNum=?", (username, hotel, roomNum))
        return True
    
    def getEmptyRoomCount(self, hotel: str) -> int:
        instanceNum = len(self.execute("SELECT * FROM rooms WHERE hotel=?", (hotel,)))
        if instanceNum == 0:
            print("Hotel {} does not exist.".format(hotel))
            return -1
        return len(self.execute("SELECT * FROM rooms WHERE hotel=? AND reservedBy=?", (hotel, '')))

class ReservationDatabase(Database):
    def __init__(self) -> None:
        super().__init__()
        self.execute("""CREATE TABLE IF NOT EXISTS reservations (
            hotel TEXT NOT NULL, 
            reservedBy TEXT NOT NULL
            fromDate TEXT NOT NULL
            toDate TEXT NOT NULL)""", tuple())