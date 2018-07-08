import sqlite3 as lite

try:
    con = lite.connect("players.db")
    cur = con.cursor()
    cur.execute("ALTER TABLE players ADD COLUMN duelsRating text")

except lite.Error as e:
    print("Database connection error")