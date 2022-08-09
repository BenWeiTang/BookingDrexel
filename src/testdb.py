from src.database import *

if __name__ == "__main__":
    hotelDB = HotelDatabase()
    reservationDB = ReservationDatabase()

    from_1 = tuple(map(lambda x: int(x), '2022-08-09'.split('-')))
    to_1 = tuple(map(lambda x: int(x), '2022-08-11'.split('-')))

    from_2 = tuple(map(lambda x: int(x), '2022-08-07'.split('-')))
    to_2 = tuple(map(lambda x: int(x), '2022-08-13'.split('-')))

    from_3 = tuple(map(lambda x: int(x), '2022-08-10'.split('-')))
    to_3 = tuple(map(lambda x: int(x), '2022-08-11'.split('-')))

    # 1
    test_from_1 = tuple(map(lambda x: int(x), '2022-08-07'.split('-')))
    test_to_1 = tuple(map(lambda x: int(x), '2022-08-09'.split('-')))

    # 0
    test_from_2 = tuple(map(lambda x: int(x), '2022-08-10'.split('-')))
    test_to_2 = tuple(map(lambda x: int(x), '2022-08-11'.split('-')))

    # 2 
    test_from_3 = tuple(map(lambda x: int(x), '2022-08-12'.split('-')))
    test_to_3 = tuple(map(lambda x: int(x), '2022-08-14'.split('-')))

    # 3 
    test_from_4 = tuple(map(lambda x: int(x), '2022-08-14'.split('-')))
    test_to_4 = tuple(map(lambda x: int(x), '2022-08-15'.split('-')))

    # 0
    test_from_5 = tuple(map(lambda x: int(x), '2022-08-09'.split('-')))
    test_to_5 = tuple(map(lambda x: int(x), '2022-08-12'.split('-')))

    # Good
    hotelDB.addHotel('abc', 5.0, 'market', 3)

    reservationDB.bookRoom('abc', 'ben', from_1, to_1)
    reservationDB.bookRoom('abc', 'ben', from_2, to_2)
    reservationDB.bookRoom('abc', 'ben', from_3, to_3)

    print('Empty Count Test 1: ' + str(reservationDB.getEmptyRoomCount('abc', test_from_1, test_to_1)) + ' (1)')
    print('Empty Count Test 2: ' + str(reservationDB.getEmptyRoomCount('abc', test_from_2, test_to_2)) + ' (0)')
    print('Empty Count Test 3: ' + str(reservationDB.getEmptyRoomCount('abc', test_from_3, test_to_3)) + ' (2)')
    print('Empty Count Test 4: ' + str(reservationDB.getEmptyRoomCount('abc', test_from_4, test_to_4)) + ' (3)')
    print('Empty Count Test 5: ' + str(reservationDB.getEmptyRoomCount('abc', test_from_5, test_to_5)) + ' (0)')

    print('Has Room Test 1: ' + str(reservationDB.hasRoom('abc', test_from_1, test_to_1)) + ' (True)')
    print('Has Room Test 2: ' + str(reservationDB.hasRoom('abc', test_from_2, test_to_2)) + ' (False)')
    print('Has Room Test 3: ' + str(reservationDB.hasRoom('abc', test_from_3, test_to_3)) + ' (True)')
    print('Has Room Test 4: ' + str(reservationDB.hasRoom('abc', test_from_4, test_to_4)) + ' (True)')
    print('Has Room Test 5: ' + str(reservationDB.hasRoom('abc', test_from_5, test_to_5)) + ' (False)')