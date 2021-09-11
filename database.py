import sqlite3
import pandas as pd
from pandas.core.frame import DataFrame
import datetime
import location
from advert import FoundAdvert, LostAdvert

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


def add_user(username: str, lat: float, lon: float, user_id):
    '''
    Add new user to database
    '''
    cursor = conn.cursor()
    cursor.execute('INSERT INTO USER(Username, Lat, Lon, Rating, UserId) VALUES (?, ?, ?, ?, ?)', (username, lat, lon, 0, user_id))
    conn.commit()


def add_lost_advert(username, text_file, photo_path):
    '''
    Add new advertisement about lost animal to database
    '''
    adv = LostAdvert.create_from_file(username, text_file)
    with open(photo_path, "rb") as file:
        photo = file.read()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO LOST(Username, Type, Sex, Date, Message, Photo)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (username, adv.type, adv.sex, adv.date, adv.get_message(), photo))
    conn.commit()
    return (adv.place, adv.get_message(), photo)


def add_found_advert(username, text_file, photo_path):
    '''
    Add new advertisement about found animal to database
    '''
    adv = FoundAdvert.create_from_file(username, text_file)
    with open(photo_path, "rb") as file:
        photo = file.read()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO FOUND(Username, Type, Sex, Date, Message, Photo)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (username, adv.type, adv.sex, adv.date, adv.get_message(), photo))
    conn.commit()
    return (adv.get_message(), photo)


def find_among_found(type: str, sex: str, lost_date: datetime.date) -> set:
    '''
    Return set of adverts where type, sex and date are fits the request
    '''
    query = f'SELECT * FROM FOUND WHERE Type = "{type}" AND (Sex = "{sex}" OR Sex = "Н") AND Date >= "{lost_date}"'
    df = pd.read_sql(query, conn)
    advert_set = set()
    for msg in df['Message']:
        photo = df[df['Message'] == msg]['Photo']
        advert_set.add((msg, photo.to_list()[0]))
    return advert_set


def find_among_lost(type: str, sex: str) -> set:
    '''
    Return set of adverts where type and sex are fits the request
    '''
    query = f'SELECT * FROM LOST WHERE Type = "{type}"'
    if sex != 'Н':
        query +=  f' AND Sex = "{sex}"'
    df = pd.read_sql(query, conn)
    advert_set = set()
    for msg in df['Message']:
        photo = df[df['Message'] == msg]['Photo']
        advert_set.add((msg, photo.to_list()[0]))
    return advert_set


def find_users_in_radius(place: str, radius: float) -> list:
    '''
    Return list of users in radius from coordinates
    '''
    coord = location.find_house_coordinates(place)
    if coord:
        df = pd.read_sql(f'SELECT * FROM USER', conn)
        df['Distance'] = df.apply(lambda x: location.find_distance(x['Lat'], x['Lon'], coord[0], coord[1]), axis = 1)
        return df[df['Distance'] <= radius]['UserId'].to_list()
    return None


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

read('LOST')
