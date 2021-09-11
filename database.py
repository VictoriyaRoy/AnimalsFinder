import sqlite3
import pandas as pd

conn = sqlite3.connect('animals.db', check_same_thread=False)

def read(table_name: str):
    '''
    Function for testing
    Print dataFrame
    '''
    df = pd.read_sql(f'SELECT * FROM {table_name}', conn)
    print(df)


def clear_table(table_name: str):
    '''
    Function for testing
    Clear dataFrame
    '''
    cursor = conn.cursor()
    cursor.execute(f"Delete from {table_name}")
    conn.commit()


def is_new_user(username: str) -> bool:
    '''
    Return True if user isn't registered yet, and Flase otherwise
    '''
    df = pd.read_sql(f'SELECT Username FROM USER WHERE Username = "{username}"', conn)
    return df.empty


def add_user(username: str, lat: float, lon: float):
    '''
    Add new user to database
    '''
    cursor = conn.cursor()
    cursor.execute('INSERT INTO USER(Username, Lat, Lon, Rating) VALUES (?, ?, ?, ?)', (username, lat, lon, 0))
    conn.commit()


def add_lost_advert(username, type, sex, name, features, date, place, photo):
    '''
    Add new advertisement about lost animal to database
    '''
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO LOST(Username, Type, Sex, Name, Features, Date, Place, Photo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (username, type, sex, name, features, date, place, photo))
    conn.commit()


def add_found_advert(username, type, sex, features, date, place, photo):
    '''
    Add new advertisement about found animal to database
    '''
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO FOUND(Username, Type, Sex, Features, Date, Place, Photo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (username, type, sex, features, date, place, photo))
    conn.commit()

# clear_table("USER")
# add_found_advert("test", "cat", "F", "Blue eyes", "24/04/21", "Lviv", "photo.jpg")
read("USER")
