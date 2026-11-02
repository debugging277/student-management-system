import sqlite3

connection = sqlite3.connect("database.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    course TEXT,
    email TEXT,
    phone TEXT,
    marks REAL
)
""")

connection.commit()
connection.close()

print("Database created successfully!")