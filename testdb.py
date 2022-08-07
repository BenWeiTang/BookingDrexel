from database import *

if __name__ == "__main__":
    pass
    usersDB = UserDataBase()
    hotelDB = HotelDatabase()
    
    # Test: adduser
    print('Test: add user')
    print(usersDB.addUser('ben', 1234))

    # Test: get user info
    print('Test: get user info')
    print(usersDB.getUserInfo('ben'))

    # Test: add room
    print('Test: add room. (True)')
    print(hotelDB.addRoom('abc', 5, 1))
    hotelDB.addRoom('abc', 5, 2)

    # Test: book room
    print('Test: book room. (True)')
    print(hotelDB.bookRoom('abc', 1, 'ben'))

    # Test: is room taken
    print('Test: is room taken. (True, False)')
    print(hotelDB.isRoomTaken('abc', 1))
    print(hotelDB.isRoomTaken('abc', 2))

    # Test: get empty room count
    print('Test: get empty room count. (1)')
    print(hotelDB.getEmptyRoomCount('abc'))

    # Test: reserved room
    print(usersDB.getReservedRooms('ben'))