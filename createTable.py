import sqlite3 as lite

#id
    #cntOfDuelWins
    #cntOfPartyWins
    #cntOfPlayedDuels
    #cntOfPlayedParties
    #totalAmountOfPlayers
    #totalSumOfPlaces
    #duelsRating

try:
    con = lite.connect("players.db")
    cur = con.cursor()
    cur.execute("""CREATE TABLE players (id text, cntOfDuelWins text, 
                    cntOfPartyWins text, cntOfPlayedDuels text, cntOfPlayedParties text, totalAmountOfPlayers text, totalSumOfPlaces text, duelsRating text)""")

except lite.Error as e:
    print("Database connection error")