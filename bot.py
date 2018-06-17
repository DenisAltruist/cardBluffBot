import telebot
import config
import json
import random
import time
import sqlite3 as lite

from __future__ import division
from telebot import types
from random import shuffle

con = None

#db variables (table players):
    #id
    #cntOfDuelWins
    #cntOfPartyWins
    #cntOfPlayedDuels
    #cntOfPlayedParties
    #totalAmountOfPlayers
    #totalSumOfPlaces


bot = telebot.TeleBot(config.token)
gamesByChatId = dict()
cardSuits = [u'\U00002764', u'\U00002666', u'\U00002660', u'\U00002663']
neutral = u'\U0001F610'
typeOfCard = {"2": 0, "3": 1, "4": 2, "5": 3, "6": 4, "7": 5, "8": 6, "9": 7, "0": 8, "j": 9, "q": 10, "k": 11, "a": 12}
playerById = dict()

def isCorrectCard(c):
    if not (c == 'j' or c == 'q' or c == 'k' or c == 'a' or c == '0' or (c >= '2' and c <= '9')):
        return False
    return True

def isCorrectSuit(c):
    if not(c >= '0' and c <= '3'):
        return False
    return True

class Stats():
    def getCursor(self):
        with lite.connect("players.db") as con:
            return con.cursor()

    def select(self, id = None):
        with lite.connect("players.db") as con:
            cur = con.cursor()
            if id is None:
                cur.execute("SELECT * FROM players")
                return cur.fetchall()
            else:
                print(id)
                cur.execute("SELECT * FROM players WHERE id = " + str(id))
                return cur.fetchall()
    
    def insert(self, data):
        with lite.connect("players.db") as con:
            cur = con.cursor()
            cur.executemany("INSERT INTO players VALUES (?,?,?,?,?,?,?)", data) 
            con.commit()

    def edit(self, id, type, newValue):
        with lite.connect("players.db") as con:
            cur = con.cursor()
            field = ""
            if type == 1:
                field = "cntOfDuelWins"
            elif type == 2:
                field = "cntOfPartyWins"
            elif type == 3:
                field = "cntOfPlayedDuels"
            elif type == 4:
                field = "cntOfPlayedParties"
            elif type == 5:
                field = "totalAmountOfPlayers"
            elif type == 6:
                field = "totalSumOfPlaces"

            sql = "UPDATE players SET " + field + " = " + str(newValue) + " WHERE id = " + str(self.id)
            cur.execute(sql)
            con.commit()


    def __init__(self, id):
        self.data = self.select(id)
        self.id = id
        if self.data == []:
            self.data = [str(id), '0', '0', '0', '0', '0', '0']
            self.insert([(str(id), '0', '0', '0', '0', '0', '0')])
        else:
            self.data = list(self.data[0])


    def change(self, tp, delta):
        self.data[tp] = str(int(self.data[tp]) + delta)
        self.edit(self.id, tp, self.data[tp])

    def addDuel(self, place):
        if place == 1:
            self.change(1, 1)
            self.change(6, 1) 
        else:
            self.change(6, 2)
        self.change(5, 2)
        self.change(3, 1)

    def addParty(self, place, numberOfPlayers):
        if place == 1:
            self.change(2, 1)
        self.change(6, place)
        self.change(5, numberOfPlayers)
        self.change(4, 1)

    def getStats(self):
        if self.data[3] == '0':
            duelWinrate = '0.00'
        else:
            print("DUEL_WINRATE")
            print(self.data[1])
            print(self.data[3])
            print(round(int(self.data[1]) / int(self.data[3]), 2))
            duelWinrate = str(round(int(self.data[1]) / int(self.data[3]) * 100, 2))

        if self.data[4] == '0':
            partyWinrate = '0.00'
        else:
            print("PARTY_WINRATE")
            partyWinrate = str(round(int(self.data[2]) / int(self.data[4]) * 100, 2))

    #id
        #cntOfDuelWins
        #cntOfPartyWins
        #cntOfPlayedDuels
        #cntOfPlayedParties
        #totalAmountOfPlayers
        #totalSumOfPlaces

        print("STATS!!!")
        print(self.data[1])
        print(self.data[2])
        print(self.data[3])
        print(self.data[4])
        print(self.data[5])
        print(self.data[6])
        cntOfPlayedGames = int(self.data[3]) + int(self.data[4])
        if (int(self.data[5]) == 0):
            val = 0.0
        else:
            bestVal = cntOfPlayedGames / int(self.data[5])
            curVal = int(self.data[6]) / int(self.data[5])
            val = (1 - curVal) / (1 - bestVal) * 100

        skill = str(round(val, 2))
        res = "Duels played: " + self.data[3] + "\n"
        res += "Duel winrate: " + duelWinrate + "%\n"
        res += "Parties played: " + self.data[4] + "\n"
        res += "Party winrate: " + partyWinrate + "%\n"
        res += "Skill: " + skill + "%\n"
        return res

class Player:
    def __init__(self, user):
        self.id = user.id

        self.first_name = user.first_name
        if (self.first_name is None):
            self.first_name = ""

        self.last_name = user.last_name
        if (self.last_name is None):
            self.last_name = ""

        self.chat_id = None
        self.isRegistered = False
        self.numberOfCards = 0
        self.stats = Stats(self.id)
    
    def join(self, game):
        self.chat_id = game.chat_id
    
    def leave(self, game):
        self.chat_id = None
        restNumberOfPlayers = len(game.alivePlayers)
        if (game.numberOfPlayers == 2 and game.numberOfRounds >= 0):
            self.stats.addDuel(restNumberOfPlayers)
        elif (game.numberOfPlayers >= 3 and game.numberOfRounds >= 0):
            self.stats.addParty(restNumberOfPlayers, game.numberOfPlayers)
    
  
    def getFullname(self):
        res = self.first_name
        if (res == ""):
            res = self.last_name
        elif self.last_name != "":
            res = res + " " + self.last_name
        return res

    def getStats(self):
        return self.getFullname() + " stats:\n" + self.stats.getStats()
    
    def sendCards(self, cardSet):
        try:
            bot.send_message(self.id, cardSet)
        except Exception as e:
            print("Sending to ban or not started user")
    
    def register(self):
        self.isRegistered = True
    
class Game:
    def __init__(self):
        self.playlist = ''
        self.numberOfPlayers = 0 #with loosers
        self.numberOfCardsInGame = 0
        self.numberOfRounds = 0
        self.isRegistered = False
        self.isStarted = False
        self.isCreated = False
        self.isFirstMove = False        
        self.alivePlayers = []
        self.players = []
        self.chat_id = None
        self.message_id = None
        self.currHand = [-1, -1, -1]
        self.currPlayer = 0
        self.cardDeck = [i for i in range(52)]
        self.keyboard = None
        self.isLooser = dict() #in the previous round
        self.startAmountOfCards = 0
        self.finishAmountOfCards = 0
        self.numberOfCards = dict()
        self.cntOfCardsByRang = dict()
        
    def isHigherHand(self, nextHand):
        if nextHand[0] < self.currHand[0]:
            return False
        elif nextHand[0] > self.currHand[0]:
            return True
        else:
            if nextHand[0] == 5:
                return nextHand[1] < self.currHand[1] 
            else:
                return nextHand > self.currHand 

    def parseStringToHand(self, s):
        s = s.lower()
        tp = int(s[0])
        if (tp <= 1) or (tp >= 3 and tp <= 4) or (tp == 7):
            return [tp, typeOfCard[s[1]], 0]
        elif tp == 2:
            firstPairType = typeOfCard[s[1]]
            secondPairType = typeOfCard[s[2]]
            if firstPairType < secondPairType:
                firstPairType, secondPairType = secondPairType, firstPairType
            return [tp, firstPairType, secondPairType]
        elif tp == 5:
            return [tp, typeOfCard[s[1]], int(s[2])]
        elif tp == 6:
            return [tp, typeOfCard[s[1]], typeOfCard[s[2]]]
        elif tp == 8:
            return [tp, typeOfCard[s[1]], int(s[2])]

    
    def getListOfPlayers(self):
        self.playlist = ''
        for player in self.players:
            self.playlist = self.playlist + self.getLinkedName(player) + '\n'
        return 'List of players: ' + str(self.numberOfPlayers) + '\n' + self.playlist
        
    def checkPlaylist(self):
        bot.edit_message_text(chat_id = self.chat_id, message_id = self.message_id, text = self.getListOfPlayers(), reply_markup = self.keyboard, parse_mode='HTML')
    
    def getName(self, player):
        res = player.first_name
        if player.last_name != '':
            res = res + ' ' + player.last_name
        return res
    
    def addPlayer(self, message, player):
        if self.players.count(player) > 0:
            self.printOut(self.getName(player) + ", you have already joined")
            return
        if not(player.chat_id is None):
            self.printOut(self.getName(player) + ", you can play only one game at a time")
            return
        if self.numberOfPlayers == config.maxNumberOfPlayers:
            self.printOut(self.getName(player) + ", the maximum number of players has been reached")
            return
        if self.isStarted:
            self.printOut(self.getName(player) + ", you can't join to the started game")
            return
        self.message_id = message.message_id #???
        self.chat_id = message.chat.id #???
        self.players.append(player)
        self.numberOfPlayers += 1
        self.checkPlaylist()
        self.numberOfCards[player] = 1
        player.join(self)
        
    def printNumberOfCards(self):
        if self.isStarted == False:
            self.printOut("The game hasn't started yet")
            return
        res = ''
        for key, value in self.numberOfCards.items():
            res = res + self.getName(key) + ": "
            if value > self.finishAmountOfCards:
                res = res + "Lost"
            else: 
                res = res + str(value)
                if (self.isLooser.get(key) == 1):
                    res = res + " " + neutral
            res = res + "\n" 
        self.printOut("Number of cards:\n" + res)

    def printOut(self, message):
        bot.send_message(self.chat_id, message, parse_mode = 'HTML')
    
    def createGame(self, message, keyboard):
        if self.isCreated:
            self.printOut("The game has been created before")
            return

        self.isCreated = True
        self.numberOfPlayers = 0
        self.keyboard = keyboard
        sentMsg = bot.send_message(self.chat_id, self.getListOfPlayers(), reply_markup = self.keyboard, parse_mode = 'HTML')
        self.chat_id = sentMsg.chat.id
        self.message_id = sentMsg.message_id
   
    def removePlayer(self, player):
        if self.isCreated == False:
            self.printOut(self.getName(player) + ", the game hasn't created yet")
            return
        if self.players.count(player) == 0:
            self.printOut(self.getName(player) + ", you haven't joined yet")
            return
        if self.isStarted:
            self.finishRound(player)
        else:
            self.numberOfCards.pop(player)
            self.players.remove(player)
            self.numberOfPlayers -= 1
            self.checkPlaylist()
            player.leave(self)
    
    def addCardToString(self, cardSet, cardNumber, isFirst):
        suit = cardNumber // 13
        rang = cardNumber % 13
        tp = ''
        if rang == 8:
            tp = '0'
        elif rang == 9:
            tp = 'J'
        elif rang == 10:
            tp = 'Q'
        elif rang == 11:
            tp = 'K'
        elif rang == 12:
            tp = 'A'
        else:
            tp = str(2 + rang)

        if isFirst == True:
            return cardSet + str(tp) + cardSuits[suit]
        else:
            return cardSet + ', ' + str(tp) + cardSuits[suit]
    
    def getLinkedName(self, player):
        nameSurname = self.getName(player)
        linkedName = '<a href="tg://user?id=' +  str(player.id) + '">' + nameSurname + '</a>'
        return linkedName
    
    def callToMove(self, player):
        self.printOut(self.getLinkedName(player) + ', your turn')

    def startRound(self):
        
        shuffle(self.alivePlayers)
        shuffle(self.cardDeck)
        for player in self.players:
            self.isLooser[player] = False

        curPos = 0
        for player in self.alivePlayers:
            cardSet = ''
            cntOfCards = self.numberOfCards[player]
            for i in range(cntOfCards):
                cardSet = self.addCardToString(cardSet, self.cardDeck[curPos], (i == 0))
                curPos += 1
            player.sendCards(cardSet)

        self.isFirstMove = True
        self.numberOfRounds += 1
        self.currPlayer = 0
        self.callToMove(self.alivePlayers[self.currPlayer])
        self.cntOfCardsByRang.clear()
        for i in range(self.numberOfCardsInGame):
            if self.cntOfCardsByRang.get(self.cardDeck[i] % 13) is None:
                self.cntOfCardsByRang[self.cardDeck[i] % 13] = 1
            else:
                self.cntOfCardsByRang[self.cardDeck[i] % 13] += 1 

    def start(self, player):
        if self.isCreated == False:
            self.printOut(self.getName(player) +  ", the game hasn't created yet")
            return
        if self.isStarted:
            self.printOut(self.getName(player) + ", the game has started yet")
            return
        if self.numberOfPlayers < 2:
            self.printOut(self.getName(player) + ", not enough players to play")
            return
        
        if self.numberOfPlayers == 2:
            self.startAmountOfCards = 5
            self.finishAmountOfCards = 9
        else:
            self.startAmountOfCards = 1
            self.finishAmountOfCards = 5

        bot.delete_message(self.chat_id, self.message_id)
        self.isStarted = True
        self.currPlayer = 0
        self.alivePlayers = self.players
        self.numberOfCardsInGame = self.numberOfPlayers * self.startAmountOfCards
        for player in self.alivePlayers:
            self.numberOfCards[player] = self.startAmountOfCards
        self.startRound()

    def firstMove(self):
        return self.isFirstMove
    
    def logMove(self):
        self.isFirstMove = False

    def isCorrectMove(self, s):
        s = s.lower()
        if len(s) == 0:
            return False
        if not (s[0] >= '0' and s[0] <= '8'):
            return False

        if (s[0] <= '1' or (s[0] >= '3' and s[0] <= '4') or s[0] == '7'):
            if len(s) != 2:
                return False
            if not isCorrectCard(s[1]):
                return False
            return True

        if len(s) != 3:
            return False

        if (s[0] == '5' or s[0] == '8'):
            if isCorrectCard(s[1]) and isCorrectSuit(s[2]):
                return True
            return False

        if (isCorrectCard(s[1]) and isCorrectCard(s[2]) and (s[1] != s[2])):
            return True
        return False

    def updateHand(self, newHand):
        self.currHand = newHand
        self.currPlayer += 1
        if self.currPlayer == len(self.alivePlayers):
            self.currPlayer = 0
        self.callToMove(self.players[self.currPlayer])
    
    def addCardsToPlayer(self, player, cnt):
        self.isLooser[player] = True
        self.numberOfCards[player] += cnt
        self.numberOfCardsInGame += cnt
        if self.numberOfCards[player] > self.finishAmountOfCards:
            player.leave(self)
            self.alivePlayers.remove(player)
            self.numberOfCardsInGame -= self.numberOfCards[player]
            

    def checkCntOf(self, rang, count):
        if self.cntOfCardsByRang.get(rang) is None:
            return False
        return (self.cntOfCardsByRang.get(rang) >= count)

    def hasHand(self):
        tp = self.currHand[0]
        res = True
        if tp == 0:
            res = self.checkCntOf(self.currHand[1], 1)
        elif tp == 1:
            res = self.checkCntOf(self.currHand[1], 2)
        elif tp == 2:
            res = self.checkCntOf(self.currHand[1], 2) and self.checkCntOf(self.currHand[2], 2)
        elif tp == 3:
            res = self.checkCntOf(self.currHand[1], 3)
        elif tp == 4:
            if self.currHand[1] < 3:
                res = False
            elif self.currHand[1] == 3:
                res = self.checkCntOf(12, 1)
                for i in range(4):
                    res = (res and self.checkCntOf(i, 1))
            else:
                for i in range (self.currHand[1] - 4, self.currHand[1] + 1):
                    res = (res and self.checkCntOf(i, 1))
        elif tp == 5:
            hasKicker = False
            cntOfGood = 0
            for i in range(self.numberOfCardsInGame):
                if (self.cardDeck[i] // 13 == self.currHand[2]) and (self.cardDeck[i] % 13 <= self.currHand[1]):
                    if (self.cardDeck[i] % 13 == self.currHand[1]):
                        hasKicker = True
                    cntOfGood += 1
            res = (cntOfGood >= 5) and (hasKicker)
        elif tp == 6:
            res = self.checkCntOf(self.currHand[1], 3) and self.checkCntOf(self.currHand[2], 2)
        elif tp == 7:
            res = self.checkCntOf(self.currHand[1], 4)
        elif tp == 8:
            if self.currHand[1] < 3:
                res = False
            elif self.currHand[1] == 3:
                cntOfGood = 0
                for i in range(self.numberOfCardsInGame):
                    rang = self.cardDeck[i] % 13
                    suit = self.cardDeck[i] // 13
                    if (suit == self.currHand[2]) and ((rang <= 3) or (rang == 12)):
                        cntOfGood += 1
                res = (cntOfGood == 5)   
            else:
                cntOfGood = 0
                for i in range(self.numberOfCardsInGame):
                    rang = self.cardDeck[i] % 13
                    suit = self.cardDeck[i] // 13
                    if (suit == self.currHand[2]) and (rang >= self.currHand[1] - 4) and (rang <= self.currHand[1]):
                        cntOfGood += 1
                res = (cntOfGood == 5)
        return res

    def reveal(self):
        res = "Hands:\n"
        curPos = 0
        for player in self.alivePlayers:
            res += self.getName(player) + ": "
            for i in range(self.numberOfCards[player]):
                res = self.addCardToString(res, self.cardDeck[curPos], (i == 0))
                curPos += 1
            res += "\n"
        self.printOut(res)

    def started(self):
        return self.isStarted

    def finish(self):
        self.alivePlayers[0].leave(self)
        self.printOut('The winner is ' + self.getLinkedName(self.alivePlayers[0]))
        self.__init__()

    def finishRound(self, leaver = None):
        self.reveal()
        if leaver is None:
            prevPlayer = self.currPlayer - 1
            if prevPlayer < 0:
                prevPlayer += len(self.alivePlayers)

            if self.hasHand():
                self.addCardsToPlayer(self.players[self.currPlayer], 1)
            else:
                self.addCardsToPlayer(self.players[prevPlayer], 1)
        else:
            self.addCardsToPlayer(leaver, self.finishAmountOfCards + 1 - self.numberOfCards[leaver])
        self.currHand = [-1, -1, -1]
        self.printNumberOfCards()
        if len(self.alivePlayers) == 1:
            self.finish()
            return
        self.startRound()

    def getChat(self, chatId):
        self.chat_id = chatId
        self.isRegistered = True

    def cancel(self):
        for player in self.players:
            player.leave(self)



def initializeFromDatabase():
    global con
    try: 
        with lite.connect("players.db") as con:
            cur = con.cursor()
    except lite.Error as e:
        print("Database connection error")

def registerPlayer(user):
    if playerById.get(user.id) is None:
        playerById[user.id] = Player(user)

def registerChat(id):
    print(id)
    if (gamesByChatId.get(id) is None) or (gamesByChatId.get(id).isRegistered == False):
        gamesByChatId[id] = Game()
        gamesByChatId[id].getChat(id)

def isAdmin(message):
    status = bot.get_chat_member(message.chat.id, message.from_user.id).status
    return (status == 'creator') or (status == 'administrator') or (message.chat.id == message.from_user.id)

@bot.message_handler(commands=['start'])
def start(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    bot.send_message(message.chat.id, "Welcome to the CardBluff bot")

@bot.message_handler(commands=['cancel'])
def cancel(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    curGame = gamesByChatId[message.chat.id]
    print(bot.get_chat_member(message.chat.id, message.from_user.id))
    if curGame.isCreated and isAdmin(message):
        curGame.cancel()
        if not curGame.isStarted:
            bot.delete_message(curGame.chat_id, curGame.message_id)
        gamesByChatId[message.chat.id] = None
        bot.send_message(message.chat.id, "Successfully canceled")

@bot.message_handler(commands=['help'])
def getHelp(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    rules = "Rules:\n"
    rules += "The game consists of few rounds. In the start of the game, each player has one card.\n"
    rules += "In the moment of playing each player has from one to five cards only knows for him\n"
    rules += "If you will have more than five cards - you will be a loser.\n"
    rules += "There is some order of moves in each round. If player has to move, he has to say new hand(it has to be higher, than current)\n"
    rules += "or say 'reveal' to check the current hand (/m - command to move, /r - command to 'reveal'). If player choose the first, he has to choose poker hand\n"
    rules += "(you can find all hands and how to move using /hands), hand must be higher than the previous one. After this, the move passes to another player\n"
    rules += "It will be a player who say 'reveal'. After that all players reveal their hands and round will be finished.\n"
    rules += "If it will be a current hand, then the current player will get an additional card in new round.\n"
    rules += "Else, the previous player will get an additional card in new round. The game goes until there is only one player\n"
    bot.send_message(message.chat.id, rules)


@bot.message_handler(commands=['stats'])
def getStats(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    if not(message.reply_to_message is None):
        msg = message.reply_to_message
        registerChat(msg.chat.id)
        registerPlayer(msg.from_user)
        bot.send_message(msg.chat.id, playerById[msg.from_user.id].getStats())
    else:
        bot.send_message(message.chat.id, playerById[message.from_user.id].getStats())


@bot.message_handler(commands=['suits'])
def getSuits(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    helplist = 'Suits:\n'
    helplist += '0 - ' + cardSuits[0] + '\n' + '1 - ' + cardSuits[1] + '\n'
    helplist += '2 - ' + cardSuits[2] + '\n' + '3 - ' + cardSuits[3] + '\n'
    bot.send_message(message.chat.id, helplist)

@bot.message_handler(commands=['hands'])
def getHands(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    helplist = 'Hands in in ascending order:\n'
    helplist += "0 - High card (example of move: /m 0K, kicker king)\n"
    helplist += "1 - One pair: (/m 18, pair of eights)\n"
    helplist += "2 - Two pairs: (/m 28J, two pairs of eights and jacks)\n"
    helplist += "3 - Three of a kind(set): (/m 3K, three kings)\n"
    helplist += "4 - Straight (five cards of sequential rank, like 23456, you have to provide highest card): (/m 46, straight up to six)\n"
    helplist += "5 - Flush (five cards with same suit, you have to provide highest card(it must be in hand!): (/m 5K0, heart flush up to king)\n"
    helplist += "Also, if the higher card is less then the hand is higher (not in like poker hands)\n"
    helplist += "6 - Full house (three cards of one rank and two cards of another one rank): (/m 6JK, three jacks and two kings)\n"
    helplist += "7 - Four of a kind (four cards of one rank): (/m 70, four tens)\n"
    helplist += "8 - Straight flush (five cards of sequential rank and same suit, you have to provide highest card and suit): (/m 8J, Straight flush up to jack)\n"
    bot.send_message(message.chat.id, helplist)

@bot.message_handler(commands=['creategame'])
def creategame(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text = "Join", callback_data = "Join")
    keyboard.add(callback_button)
    gamesByChatId[message.chat.id].createGame(message, keyboard)
   
@bot.callback_query_handler(func=lambda c: True)
def inline(c):
    if c.data == 'Join':
        registerPlayer(c.from_user)
        registerChat(c.message.chat.id)
        gamesByChatId[c.message.chat.id].addPlayer(c.message, playerById[c.from_user.id]) 

@bot.message_handler(commands=['leavegame'])
def leavegame(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    gamesByChatId[message.chat.id].removePlayer(playerById[message.from_user.id]) 

@bot.message_handler(commands=['countcards'])
def countcards(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    gamesByChatId[message.chat.id].printNumberOfCards()

@bot.message_handler(commands=['startgame'])
def startgame(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    gamesByChatId[message.chat.id].start(playerById[message.from_user.id])

@bot.message_handler(commands=['r'])
def getmsg(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    global gamesByChatId
    currGame = gamesByChatId[message.chat.id]
    currPlayer = playerById[message.from_user.id]
    if (not currGame.isCreated or not currGame.isStarted):
        return
    if (currPlayer != currGame.players[currGame.currPlayer]):
        return
    if currGame.firstMove():
        currGame.printOut("You can't reveal at the first move")
    else:
        currGame.finishRound()   
    gamesByChatId[message.chat.id] = currGame

@bot.message_handler(commands=['m'])
def getmessage(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    global gamesByChatId
    currGame = gamesByChatId[message.chat.id]
    currText = message.text[3:]
    currPlayer = playerById[message.from_user.id]
    if (not currGame.isStarted):
        return 
    if (currPlayer != currGame.alivePlayers[currGame.currPlayer]):
        return
    if currGame.isCorrectMove(currText) and currGame.started():
        if not currGame.isHigherHand(currGame.parseStringToHand(currText)):
            currGame.printOut("It's a not higher than current")
        else:                
            currGame.updateHand(currGame.parseStringToHand(currText))
        currGame.logMove()
    else: 
        if currGame.isStarted:
            currGame.printOut("Incorrect move")
    gamesByChatId[message.chat.id] = currGame


@bot.message_handler(content_types = ['text'])
def getm(message):
    print(message.from_user.id)
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    if (message.text == "go"):
        bot.send_message(message.chat.id, "successfully")
        print(message.from_user.id)
        playerById[message.from_user.id].register()

initializeFromDatabase()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print("Internet error")
        time.sleep(5)

