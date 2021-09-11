import sqlite3
import pandas as pd
from pandas.core.frame import DataFrame
import datetime

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


def add_lost_advert(username, type, sex, name, features, lost_date, place, photo):
    '''
    Add new advertisement about lost animal to database
    '''
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO LOST(Username, Type, Sex, Name, Features, Date, Place, Photo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (username, type, sex, name, features, lost_date, place, photo))
    conn.commit()


def add_found_advert(username, type, sex, features, place, photo):
    '''
    Add new advertisement about found animal to database
    '''
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO FOUND(Username, Type, Sex, Features, Date, Place, Photo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (username, type, sex, features, datetime.date.today(), place, photo))
    conn.commit()


def find_among_found(type: str, sex: str, lost_date: datetime.date) -> DataFrame:
    '''
    Return DataFrame of adverts where type, sex and date are fits the request
    '''
    query = f'SELECT * FROM FOUND WHERE Type = "{type}" AND (Sex = "{sex}" OR Sex IS NULL) AND Date >= "{lost_date}"'
    df = pd.read_sql(query, conn)
    return df


def find_among_lost(type: str, sex: str) -> DataFrame:
    '''
    Return DataFrame of adverts where type and sex are fits the request
    '''
    query = f'SELECT * FROM LOST WHERE Type = "{type}"'
    if sex:
        query +=  f' AND Sex = "{sex}"'
    df = pd.read_sql(query, conn)
    return df
