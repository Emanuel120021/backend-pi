import sqlite3

conn = sqlite3.connect ('banco.db')
cursor = conn.cursor()

cursor.execute('''
               CREATE TABLE IF NOT EXISTS usuarios(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')

cursor.execute("INSERT INTO usuarios (username, password) VALUES (?,?)", ("admin", "1234"))
conn.commit()
conn.close