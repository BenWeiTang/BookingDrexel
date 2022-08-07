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
            uid INTEGER NOT NULL,
            username TEXT NOT NULL, 
            password TEXT NOT NULL)""", tuple())
        
    def hasUserByName(self, username: str) -> bool:
        instanceNum = len(self.execute("SELECT * FROM users WHERE username=?", (username,)))
        return instanceNum != 0
    
    def hasUserById(self, uid: int) -> bool:
        instanceNum = len(self.execute("SELECT * FROM users WHERE uid=?", (uid,)))
        return instanceNum != 0
    
    def addUser(self, username: str, password: str) -> bool:
        if self.hasUserByName(username):
            print("User {} already exists.".format(username))
            return False 
        uid = hash(username)
        self.execute("INSERT INTO users VALUES (?, ?, ?)", (uid, username, password))
        return True

    def getUserInfo(self, username: str) -> dict:
        if not self.hasUserByName(username):
            print("User {} does not exist.".format(username))
            return None 
        data = self.execute("SELECT * FROM users WHERE username=?", (username,))[0]
        return {'uid': data[0], 'username': data[1], 'password': data[2]}

    # Only works on file not RAM db
    def getReservedRooms(self, uid: int) -> list:
        if not self.hasUserById(uid):
            print("Cannot find user with uid {}.".format(uid))
            return None
        return self.execute("SELECT * FROM rooms WHERE reservedBy=?", (uid,))

class HotelDatabase(Database):
    def __init__(self) -> None:
        super().__init__()
        self.execute("""CREATE TABLE IF NOT EXISTS rooms (
            hotel TEXT NOT NULL, 
            rating REAL NOT NULL,
            roomNum INTEGER NOT NULL,
            reservedBy INTEGER NOT NULL)""", tuple())
    
    def hasRoom(self, hotel: str, roomNum: int) -> None:
        instanceNum = len(self.execute("SELECT * FROM rooms WHERE hotel=? AND roomNum=?", (hotel, roomNum)))
        return instanceNum != 0
    
    def isRoomTaken(self, hotel: str, roomNum: int) -> bool:
        if not self.hasRoom(hotel, roomNum):
            print("Hotel room {} {} does not exist.".format(hotel, roomNum))
            return
        taken = self.execute("SELECT reservedBy FROM rooms WHERE hotel=? AND roomNum=?", (hotel, roomNum))
        return taken[0][0] != -1

    def addRoom(self, hotel: str, rating: float, roomNum: int) -> None:
        if self.hasRoom(hotel, roomNum):
            print("Hotel room {} {} already exist.".format(hotel, roomNum))
            return
        self.execute("INSERT INTO rooms VALUES (?, ?, ?, ?)", (hotel, rating, roomNum, -1))
    
    def bookRoom(self, hotel: str, roomNum: int, uid: int) -> None:
        if not self.hasRoom(hotel, roomNum):
            print("Hotel room {} {} does not exist.".format(hotel, roomNum))
            return
        self.execute("UPDATE rooms SET reservedBy=? WHERE hotel=? AND roomNum=?", (uid, hotel, roomNum))
    
    def getEmptyRoomCount(self, hotel: str) -> int:
        instanceNum = len(self.execute("SELECT * FROM rooms WHERE hotel=?", (hotel,)))
        if instanceNum == 0:
            print("Hotel {} does not exist.".format(hotel))
            return -1
        return len(self.execute("SELECT * FROM rooms WHERE hotel=? AND reservedBy=?", (hotel, -1)))