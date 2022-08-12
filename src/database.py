from datetime import date
import sqlite3

class Database:
    def __init__(self):
        # self.conn = sqlite3.connect(':memory:')
        # Be careful with this
        self.conn = sqlite3.connect('BookingDrexel.db', check_same_thread=False)
        self.execute("""CREATE TABLE IF NOT EXISTS users (
            username TEXT NOT NULL, 
            password TEXT NOT NULL)""", tuple())
        self.execute("""CREATE TABLE IF NOT EXISTS rooms (
            hotel TEXT NOT NULL, 
            rating REAL NOT NULL,
            location TEXT NOT NULL,
            roomCount INTEGER NOT NULL)""", tuple())
        self.execute("""CREATE TABLE IF NOT EXISTS reservations (
            hotel TEXT NOT NULL,
            reservedBy TEXT NOT NULL,
            fromDate TEXT NOT NULL,
            toDate TEXT NOT NULL)""", tuple())
        self.execute("""CREATE TABLE IF NOT EXISTS wishlists (
            hotel TEXT NOT NULL,
            madeBy TEXT NOT NULL,
            fromDate TEXT NOT NULL,
            toDate TEXT NOT NULL,
            available TEXT NOT NULL)""", tuple())
    
    def __del__(self):
        self.conn.close()
    
    def execute(self, sql: str, parameters: tuple):
        result = None
        with self.conn:
            c = self.conn.cursor()
            c.execute(sql, parameters)
            result = c.fetchall()
        return result
    
    def dateTupToStr(self, tupDate: tuple) -> str:
        return date(tupDate[0], tupDate[1], tupDate[2]).isoformat()
    
    def dateStrToTup(self, strDate: str) -> tuple:
        result = date.fromisoformat(strDate)
        return (result.year, result.month, result.day)
    
    def hasUser(self, username: str) -> bool:
        instanceNum = len(self.execute("SELECT * FROM users WHERE username=?", (username,)))
        return instanceNum != 0
    
    def hasHotel(self, hotel: str) -> bool:
        instanceNum = len(self.execute("SELECT * FROM rooms WHERE hotel=?", (hotel,)))
        return instanceNum != 0
    
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
     
    def hasRoom(self, hotel: str, fromDate: tuple, toDate: tuple) -> bool:
        return self.getEmptyRoomCount(hotel, fromDate, toDate) != 0
    
    def userIntegrityCheck(self, username: str, database: str) -> bool:
        if not self.hasUser(username):
            print("[{}] User {} does not exist in the database.".format(database, username))
            return False
        return True
    
    def hotelIntegrityCheck(self, hotel: str, database: str) -> bool:
        if not self.hasHotel(hotel):
            print("[{}] Hotel {} does not exist in the database.".format(database, hotel))
            return False
        return True

class UserDatabase(Database):
    def __init__(self) -> None:
        super().__init__()
        
    def addUser(self, username: str, password: str) -> bool:
        if self.hasUser(username):
            print("[User DB] User {} already exists.".format(username))
            return False 
        self.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        return True
    
    def removeUser(self, useranme: str) -> bool:
        if not self.userIntegrityCheck(useranme, "User BD"):
            return False
        self.execute("DELETE FROM users WHERE username=?", (useranme,))
        return True

    def getUserInfo(self, username: str) -> dict:
        if not self.userIntegrityCheck(username, "User DB"):
            return None 
        data = self.execute("SELECT * FROM users WHERE username=?", (username,))[0]
        return {'username': data[0], 'password': data[1]}

    # Only works on file not RAM db
    def getReservedRooms(self, username: str) -> list:
        rooms = self.execute("SELECT * FROM rooms WHERE reservedBy=?", (username,))
        result = list()
        for room in rooms:
            result.append({'hotel': room[0], 'rating': room[1], 'location': room[2]})
        return result

class HotelDatabase(Database):
    def __init__(self) -> None:
        super().__init__()
    
    def addHotel(self, hotel: str, rating: float, location: str, roomCount: int) -> bool:
        if self.hasHotel(hotel):
            print("[Hotel DB] Hotel {} already exists.".format(hotel))
            return False
        self.execute("INSERT INTO rooms VALUES (?, ?, ?, ?)", (hotel, rating, location, roomCount))
        return True
    
    def removeHotel(self, hotel: str) -> bool:
        if not self.hotelIntegrityCheck(hotel, "Hotel BD"):
            return False
        self.execute("DELETE FROM rooms WHERE hotel=?", (hotel,))
        return True

class ReservationDatabase(Database):
    def __init__(self) -> None:
        super().__init__()
    
    def bookRoom(self, username: str, hotel: str, fromDate: tuple, toDate: tuple) -> bool:
        if not self.userIntegrityCheck(username, "Reservation DB"):
            return False
        if not self.hotelIntegrityCheck(hotel, "Reservation DB"):
            return False
        fromStr = self.dateTupToStr(fromDate)
        toStr = self.dateTupToStr(toDate)
        if not self.hasRoom(hotel, fromDate, toDate):
            print("[Reservation DB] Reservation from {} to {} is not availabel.".format(fromStr, toStr))
            return False
        self.execute("INSERT INTO reservations VALUES (?, ?, ?, ?)", (hotel, username, fromStr, toStr))
        return True
    
    def cancelRoom(self, username: str, hotel: str, fromDate: tuple, toDate:tuple) -> bool:
        if not self.userIntegrityCheck(username, "Reservation DB"):
            return False
        if not self.hotelIntegrityCheck(hotel, "Reservation DB"):
            return False
        fromStr = self.dateTupToStr(fromDate)
        toStr = self.dateTupToStr(toDate)
        instanceNum = len(self.execute("""SELECT * FROM reservations
            WHERE hotel=?
            AND reservedBy=?
            AND fromDate=?
            AND toDate=?""", (hotel, username, fromStr, toStr)))
        if instanceNum == 0:
            print("[Reservation DB] Cannot found reservation at {} by {} from {} to {}".format(hotel, username, fromStr, toStr))
            return False
        self.execute("""DELETE FROM reservations
            WHERE hotel=?
            AND reservedBy=?
            AND fromDate=?
            AND toDate=?""", (hotel, username, fromStr, toStr))
        return True
        

class WishlistDatabase(Database):
    def __init__(self):
        super().__init__()
    
    def addWishlist(self, username: str, hotel: str, fromDate: tuple, toDate: tuple) -> bool:
        if not self.userIntegrityCheck(username, "Wishlist DB"):
            return False
        if not self.hotelIntegrityCheck(hotel, "Wishlist DB"):
            return False
        fromStr = self.dateTupToStr(fromDate)
        toStr = self.dateTupToStr(toDate)
        isAvailable = str(self.hasRoom(hotel, fromDate, toDate))
        self.execute("INSERT INTO wishlists VALUES (?, ?, ?, ?, ?)", (hotel, username, fromStr, toStr, isAvailable))
        return True 

    def removeWishlist(self, username: str, hotel: str, fromDate: tuple, toDate: tuple) -> bool:
        if not self.userIntegrityCheck(username, "Wishlist DB"):
            return False
        if not self.hotelIntegrityCheck(hotel, "Wishlist DB"):
            return False
        fromStr = self.dateTupToStr(fromDate)
        toStr = self.dateTupToStr(toDate)
        instanceNum = len(self.execute("""SELECT * FROM wishlists
            WHERE hotel=?
            AND madeBy=?
            AND fromDate=?
            AND toDate=?""", (hotel, username, fromStr, toStr)))
        if instanceNum == 0:
            print("[Wishlist DB] Cannot found wishlist at {} by {} from {} to {}".format(hotel, username, fromStr, toStr))
            return None
        self.execute("""DELETE FROM wishlists 
            WHERE hotel=? 
            AND madeBy=? 
            AND fromDate=? 
            AND toDate=?""", (hotel, username, fromStr, toStr))
        return True

    def refreshWishlist(self, username: str) -> None:
        if not self.userIntegrityCheck(username, "Wishlist DB"):
            return False
        allWishlists = self.execute("SELECT hotel, fromDate, toDate FROM wishlists WHERE madeBy=?", (username,))
        for wl in allWishlists:
            fromTup = self.dateStrToTup(wl[1])
            toTup = self.dateStrToTup(wl[2])
            isAvailable = str(self.hasRoom(wl[0], fromTup, toTup))
            self.execute("""UPDATE wishlists SET available=?
            WHERE madeBy=?
            AND hotel=?
            AND fromDate=?
            AND toDate=?""", (isAvailable, username, wl[0], wl[1], wl[2]))
    
    def getWishList(self, username: str) -> list:
        if not self.userIntegrityCheck(username, "Wishlist DB"):
            return False
        self.refreshWishlist(username)
        allWishlists = self.execute("SELECT * FROM wishlists WHERE madeBy=?", (username,))
        result = list()
        for wl in allWishlists:
            result.append({'hotel': wl[0], 'username': wl[1], 'fromDate': wl[2], 'toDate': wl[3], 'available': wl[4]})
        return result