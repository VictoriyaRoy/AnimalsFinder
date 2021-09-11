import sqlite3
import pandas as pd

conn = sqlite3.connect('animals.db', check_same_thread=False)

def create():
    df_users = pd.DataFrame(columns=['Username', "Lat", "Lon"])
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

def is_new_user(username: str) -> bool:
    df = pd.read_sql(f'SELECT Username FROM USER WHERE Username = "{username}"', conn)
    return df.empty

def add_user(username, lat, lon):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO USER(Username, Lat, Lon) VALUES (?, ?, ?)', (username, lat, lon))
    conn.commit()


# create()
# clear_table()

# if is_new_user("test_user"):
#     add_user("test_user", 0, 0)
#     print('Success')
#     read()
# else:
#     print("Error")
