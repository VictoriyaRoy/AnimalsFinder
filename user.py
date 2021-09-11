import sqlite3
import pandas as pd

conn = sqlite3.connect('animals.db')

def create():
    df_users = pd.DataFrame(columns=['Nickname', "Lat", "Lon"])
    df_users.to_sql('USER', conn)

def read():
    df = pd.read_sql('''
    SELECT *
    FROM USER
''', conn)
    print(df)

def clear_table():
    cursor = conn.cursor()
    cursor.execute("Delete from USER")
    conn.commit()

def is_new_user(nickname: str) -> bool:
    df = pd.read_sql(f'SELECT Nickname FROM USER WHERE Nickname = "{nickname}"', conn)
    return df.empty

def add_user(nickname, lat, lon):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO USER(Nickname, Lat, Lon) VALUES (?, ?, ?)', (nickname, lat, lon))
    conn.commit()


# create()
# clear_table()

if is_new_user("test_user"):
    add_user("test_user", 0, 0)
    print('Success')
    read()
else:
    print("Error")
