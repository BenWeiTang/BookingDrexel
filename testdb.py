from socket import htonl
from database import *

if __name__ == "__main__":
    usersDB = UserDataBase()
    usersDB.addUser("Ben", 1234)
    uid = usersDB.getUserInfo("Ben")[0]

    hotelDB = HotelDatabase()
    hotelDB.addRoom("abc", 0.0, 1)
    hotelDB.addRoom("def", 0.0, 99)
    hotelDB.bookRoom("abc", 1, uid)
    hotelDB.bookRoom("def", 99, uid)

    print(usersDB.getReservedRooms(uid))