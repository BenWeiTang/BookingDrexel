from datetime import date
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
    
    def hasRoom(self, hotel: str, fromDate: str, toDate: str) -> bool:
        return self.getEmptyRoomCount(hotel, fromDate, toDate) != 0

    def bookRoom(self, hotel: str, username: str, fromYear: int, fromMonth: int, fromDay: int, toYear: int, toMonth: int, toDay: int) -> bool:
        fromDate = date.fromisoformat("{}-{}-{}".format(fromYear, fromMonth, fromDay))
        toDate = date.fromisoformat("{}-{}-{}".format(toYear, toMonth, toDay))
        fromStr = fromDate.isoformat()
        toStr = toDate.isoformat()
        if not self.hasRoom(fromStr, toStr):
            print("Reservation from {} to {} is not availabel.".format(fromStr, toStr))
            return False
        self.execute("INSTER INTO reservations VALUES (?, ?, ?, ?)", (hotel, username, fromStr, toStr))
        return True

    def getEmptyRoomCount(self, hotel: str, fromDate: str, toDate: str) -> int:
        roomCount = self.execute("SELECT roomCount FROM rooms WHERE hotel=?", (hotel,))[0][0]
        targetSlotAvailableCount = roomCount
        aFrom = date.fromisoformat(fromDate)
        aTo = date.fromisoformat(toDate)
        allRes = self.execute("SELECT fromDate, toDate FROM reservations WHERE hotel=?", (hotel,))
        for res in allRes:
            bFrom = date.fromisoformat(res[0])
            bTo = date.fromisoformat(res[1])
            if aFrom < bTo and aTo > bFrom:
                print("Overlap")
                targetSlotAvailableCount -= 1
        return targetSlotAvailableCount 