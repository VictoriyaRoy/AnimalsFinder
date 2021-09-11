import sqlite3
import pandas as pd

conn = sqlite3.connect('animals.db', check_same_thread=False)

def create_user():
    df_users = pd.DataFrame(columns=["Username", "Lat", "Lon"])
    df_users.to_sql('USER', conn)

def create_lost():
    df_lost = pd.DataFrame(columns=["Username", "Type", "Sex", "Name", "Features", "Date", "Place", "Photo"])
    df_lost.to_sql('LOST', conn)

def read(table_name):
    df = pd.read_sql(f'SELECT * FROM {table_name}', conn)
    print(df)

def clear_table(table_name):
    cursor = conn.cursor()
    cursor.execute(f"Delete from {table_name}")
    conn.commit()

def is_new_user(username: str) -> bool:
    df = pd.read_sql(f'SELECT Username FROM USER WHERE Username = "{username}"', conn)
    return df.empty

def add_user(username, lat, lon):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO USER(Username, Lat, Lon) VALUES (?, ?, ?)', (username, lat, lon))
    conn.commit()

def add_lost_advert(username, type, sex, name, features, date, place, photo):
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO LOST(Username, Type, Sex, Name, Features, Date, Place, Photo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (username, type, sex, name, features, date, place, photo))
    conn.commit()


# create_lost()
# clear_table("LOST")
add_lost_advert("test", "cat", "F", "Levchik", "Blue eyes", "24/04/21", "Lviv", "photo.jpg")
read("LOST")
