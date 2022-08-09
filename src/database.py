from datetime import date
import sqlite3

class Database:
    def __init__(self):
        # Be careful with this
        self.conn = sqlite3.connect('BookingDrexel.db', check_same_thread=False)
        # self.conn = sqlite3.connect(':memory:')
    
    def __del__(self):
        self.conn.close()
    
    def execute(self, sql: str, parameters: tuple):
        result = None
        with self.conn:
            c = self.conn.cursor()
            c.execute(sql, parameters)
            result = c.fetchall()
        return result
    
    # Need testing
    def dateTupToStr(self, tupDate: tuple) -> str:
        return date(tupDate[0, tupDate[1], tupDate[2]]).isoformat()
    
    # Need testing
    def dateStrToTup(self, strDate: str) -> tuple:
        result = date.fromisoformat(strDate)
        return tuple(result.year, result.month, result.day)
  
class UserDatabase(Database):
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

class ReservationDatabase(Database):
    def __init__(self) -> None:
        super().__init__()
        self.execute("""CREATE TABLE IF NOT EXISTS reservations (
            hotel TEXT NOT NULL,
            reservedBy TEXT NOT NULL,
            fromDate TEXT NOT NULL,
            toDate TEXT NOT NULL)""", tuple())
    
    def hasRoom(self, hotel: str, fromDate: tuple, toDate: tuple) -> bool:
        return self.getEmptyRoomCount(hotel, fromDate, toDate) != 0

    def bookRoom(self, hotel: str, username: str, fromDate: tuple, toDate: tuple) -> bool:
        fromStr = self.dateTupToStr(fromDate)
        toStr = self.dateTupToStr(toDate)
        if not self.hasRoom(hotel, fromDate, toDate):
            print("Reservation from {} to {} is not availabel.".format(fromStr, toStr))
            return False
        self.execute("INSERT INTO reservations VALUES (?, ?, ?, ?)", (hotel, username, fromStr, toStr))
        return True

    def getEmptyRoomCount(self, hotel: str, fromDate: tuple, toDate: tuple) -> int:
        roomCount = self.execute("SELECT roomCount FROM rooms WHERE hotel=?", (hotel,))[0][0]
        targetSlotAvailableCount = roomCount
        aFrom = date(fromDate[0], fromDate[1], fromDate[2])
        aTo = date(toDate[0], toDate[1], toDate[2])
        allRes = self.execute("SELECT fromDate, toDate FROM reservations WHERE hotel=?", (hotel,))
        for res in allRes:
            bFrom = date.fromisoformat(res[0])
            bTo = date.fromisoformat(res[1])
            if aFrom <= bTo and aTo >= bFrom:
                targetSlotAvailableCount -= 1
        return targetSlotAvailableCount 

class WishlistDatabase(Database):
    def __init__(self):
        super().__init__()
        self.execute("""CREATE TABLE IF NOT EXISTS wishlists (
            hotel TEXT NOT NULL,
            madeBy TEXT NOT NULL,
            fromDate TEXT NOT NULL,
            toDate TEXT NOT NULL,
            available TEXT NOT NULL)""", tuple())
    
    def addWishlist(self, username: str, hotel: str, fromDate: tuple, toDate: tuple, rvDB: ReservationDatabase) -> None:
        fromStr = self.dateTupToStr(fromDate)
        toStr = self.dateTupToStr(toDate)
        isAvailable = str(rvDB.hasRoom(hotel, fromDate, toDate))
        self.execute("INSERT INTO wishlists VALUES (?, ?, ?, ?, ?)", (hotel, username, fromStr, toStr, isAvailable))

    def removeWishlist(self, username: str, hotel: str, fromDate: tuple, toDate: tuple) -> None:
        fromStr = self.dateTupToStr(fromDate)
        toStr = self.dateTupToStr(toDate)
        self.execute("""DELETE FROM wishlists 
            WHERE hotel=? 
            AND madeBy=? 
            AND fromDate=? 
            AND toDate=?""", (hotel, username, fromStr, toStr))

    def refreshWishlist(self, username: str, rvDB: ReservationDatabase) -> None:
        allWishlists = self.execute("SELECT hotel, fromDate, toDate FROM wishlists WHERE madeBy=?", (username,))
        for wl in allWishlists:
            fromTup = self.dateStrToTup(wl[1])
            toTup = self.dateStrToTup(wl[2])
            isAvailable = str(rvDB.hasRoom(wl[0], fromTup, toTup))
            self.execute("""UPDATE wishlists SET available=?
            WHERE madeBy=?
            AND hotel=?
            AND fromDate=?
            AND toDate=?""", (isAvailable, username, wl[0], wl[1], wl[2]))
    
    def getWishList(self, username: str, rvDB: ReservationDatabase) -> list:
        self.refreshWishlist(username, rvDB)
        allWishlists = self.execute("SELECT * FROM wishlists WHERE madeBy=?", (username,))
        result = list()
        for wl in allWishlists:
            result.append({'hotel': wl[0], 'username': wl[1], 'fromDate': wl[2], 'toDate': wl[3], 'available': wl[4]})
        return result