import sqlite3
import pandas as pd
from pandas.core.frame import DataFrame
import datetime
import location
from advert import FoundAdvert

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
    print(type(lat))
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


def find_among_found(type: str, sex: str, lost_date: datetime.date) -> set:
    '''
    Return set of adverts where type, sex and date are fits the request
    '''
    query = f'SELECT * FROM FOUND WHERE Type = "{type}" AND (Sex = "{sex}" OR Sex IS NULL) AND Date >= "{lost_date}"'
    df = pd.read_sql(query, conn)
    df['Advert'] = df.apply(lambda x: FoundAdvert(x['Username'], x['Type'], x['Sex'], x['Features'], x['Date'], x['Place'], x['Photo']), axis = 1)
    advert_set = set()
    for adv in df['Advert']:
        advert_set.add((adv.get_message(), None))
    return advert_set


def find_among_lost(type: str, sex: str) -> DataFrame:
    '''
    Return DataFrame of adverts where type and sex are fits the request
    '''
    query = f'SELECT * FROM LOST WHERE Type = "{type}"'
    if sex:
        query +=  f' AND Sex = "{sex}"'
    df = pd.read_sql(query, conn)
    return df


def find_users_in_radius(lat: float, lon: float, radius: float) -> list:
    '''
    Return list of users in radius from coordinates
    '''
    df = pd.read_sql(f'SELECT * FROM USER', conn)
    df['Distance'] = df.apply(lambda x: location.find_distance(x['Lat'], x['Lon'], lat, lon), axis = 1)
    return df[df['Distance'] <= radius]['Username'].to_list()


def lost_animals_of_user(username: str) -> dict:
    '''
    Return list of animals of user
    '''
    query = f'SELECT Name FROM LOST WHERE Username = "{username}"'
    df = pd.read_sql(query, conn)
    return set(df['Name'].to_list())


def delete_lost_advert(username: str, animal_name: str):
    '''
    Delete lost advert when animal was found
    '''
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM Lost WHERE Username = "{username}" AND Name = "{animal_name}"')
    conn.commit()

# add_found_advert("victoriya_roi", "Кіт", "Ч", "Котик Садового", "Площа Ринок", None)
# read("FOUND")