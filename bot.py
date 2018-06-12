import telebot
import config
import json
import random
import time

from telebot import types
from random import shuffle

bot = telebot.TeleBot(config.token)
chatsById = dict()
gamesByChatId = dict()
isJoined = dict()
firstNameById = dict()
lastNameById = dict()
users = dict()
cardSuits = [u'\U00002665', u'\U00002666', u'\U00002660', u'\U00002663']
neutral = u'\U0001F610'
typeOfCard = {"2": 0, "3": 1, "4": 2, "5": 3, "6": 4, "7": 5, "8": 6, "9": 7, "0": 8, "J": 9, "Q": 10, "K": 11, "A": 12}

def isCorrectCard(c):
    if not (c == 'J' or c == 'Q' or c == 'K' or c == 'A' or c == '0' or (c >= '2' and c <= '9')):
        return False
    return True

def isCorrectSuit(c):
    if not(c >= '0' and c <= '3'):
        return False
    return True
    
class Game:
    def __init__(self):
        self.numberOfPlayers = 0
        self.numberOfCardsInGame = 0
        self.playlist = ''
        self.id = []
        self.alivePlayers = []
        self.isStarted = False
        self.isCreated = False
        self.isFirstMove = False
        self.chat_id = -1
        self.message_id = -1
        self.currHand = [-1, -1, -1]
        self.numberOfCards = dict()
        self.cntOfCardsByRang = dict()
        self.isLooser = dict()
        self.currPlayer = 0
        self.cardDeck = [i for i in range(52)]
        self.keyboard = None

        
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
        for currentId in self.id:
            self.playlist = self.playlist + self.getLinkedName(currentId) + '\n'
        return 'List of players: ' + str(self.numberOfPlayers) + '\n' + self.playlist
        
    def checkPlaylist(self):
        bot.edit_message_text(chat_id = self.chat_id, message_id = self.message_id, text = self.getListOfPlayers(), reply_markup = self.keyboard, parse_mode='HTML')
    
    def getName(self, id):
        res = firstNameById[id]
        if lastNameById[id] != '':
            res = res + ' ' + lastNameById[id]
        return res
    
    def addPlayer(self, message, from_user):
        if isJoined.get(from_user.id) == 1:
            self.printOut(self.getName(from_user.id) + ", you can play only one game at a time")
            return
        if self.id.count(from_user.id) > 0:
            self.printOut(self.getName(from_user.id) + ", you have already joined")
            return
        if self.numberOfPlayers == config.maxNumberOfPlayers:
            self.printOut(self.getName(from_user.id) + ", the maximum number of players has been reached")
        if self.isStarted:
            self.printOut(self.getName(from_user.id) + ", you can't join to the started game")
            return

        isJoined[from_user.id] = 1
        self.numberOfCards[from_user.id] = 1
        self.id.append(from_user.id)
        self.numberOfPlayers += 1

        self.message_id = message.message_id
        self.chat_id = message.chat.id
        
        self.playlist = self.playlist + '\n' + self.getLinkedName(from_user.id)
        self.checkPlaylist()
    
    def printNumberOfCards(self):
        if self.isCreated == False:
            self.printOut("The game hasn't created yet")
            return
        res = ''
        for key, value in self.numberOfCards.items():
            res = res + self.getName(key) + ": "
            if value > 5:
                res = res + "Lost"
            else: 
                res = res + str(value)
                if not (self.isLooser.get(key) is None) and not(self.isLooser.get(key) == 0):
                    res = res + " " + neutral
            res = res + "\n" 
        self.printOut("Number of cards:\n" + res)

    def printOut(self, message):
        bot.send_message(self.chat_id, message, parse_mode='HTML')
    
    def createGame(self, message, keyboard):
        if self.isCreated:
            self.printOut("The game has been created before")
            return
        self.isCreated = True
        self.numberOfPlayers = 0
        self.keyboard = keyboard
        
        sentMsg = bot.send_message(self.chat_id, self.getListOfPlayers(), reply_markup = self.keyboard, parse_mode='HTML')
        self.chat_id = sentMsg.chat.id
        self.message_id = sentMsg.message_id
   
    def removePlayer(self, message):
        curId = message.from_user.id
        if self.isCreated == False:
            self.printOut(self.getName(curId) + ", the game hasn't created yet")
            return
        if self.id.count(curId) == 0:
            self.printOut(self.getName(curId) + ", you haven't joined yet")
            return
        if self.isStarted:
            self.printOut(self.getName(curId) + ", you can't leave from the started game")
            return
        isJoined[message.from_user.id] = 0
        self.numberOfCards.pop(message.from_user.id)
        self.id.remove(message.from_user.id)
        self.numberOfPlayers -= 1
        self.checkPlaylist()
    
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
    
    def getLinkedName(self, id):
        nameSurname = self.getName(id)
        linkedName = '<a href="tg://user?id=' +  str(id) + '">' + nameSurname + '</a>'
        return linkedName
    
    def callToMove(self, id):
        self.printOut(self.getLinkedName(id) + ', your turn')

    def startRound(self):
        shuffle(self.id)
        shuffle(self.cardDeck)
        for curId in self.id:
            self.isLooser[curId] = 0
        curPos = 0
        for currId in self.alivePlayers:
            cardSet = ''
            cntOfCards = self.numberOfCards[currId]
            for i in range(cntOfCards):
                cardSet = self.addCardToString(cardSet, self.cardDeck[curPos], (i == 0))
                curPos += 1
            bot.send_message(chatsById[currId], cardSet)
        self.isFirstMove = True
        self.currPlayer = 0
        self.callToMove(self.id[self.currPlayer])
        self.cntOfCardsByRang.clear()
        for i in range(self.numberOfCardsInGame):
            if self.cntOfCardsByRang.get(self.cardDeck[i] % 13) is None:
                self.cntOfCardsByRang[self.cardDeck[i] % 13] = 1
            else:
                self.cntOfCardsByRang[self.cardDeck[i] % 13] += 1 

    def start(self, message):
        curId = message.from_user.id
        if self.isCreated == False:
            self.printOut(self.getName(curId) +  ", the game hasn't created yet")
            return
        if self.isStarted:
            self.printOut(self.getName(curId) + ", the game has started yet")
            return
        if self.numberOfPlayers < 1:
            self.printOut(self.getName(curId) + ", not enough players to play")
            return
        listOfNonInitialized = ''
        for index in range(0, len(self.id)):
            currId = self.id[index]
            if chatsById.get(currId) == None:
                listOfNonInitialized += self.getLinkedName(currId) + ', '
        if listOfNonInitialized != '':
            self.printOut(listOfNonInitialized + "please, send 'go' to the CardBluff bot")
            return
        self.printOut("The game has started")
        bot.delete_message(self.chat_id, self.message_id)
        self.isStarted = True
        self.currPlayer = 0
        self.alivePlayers = self.id
        self.numberOfCardsInGame = self.numberOfPlayers
        self.startRound()

    def firstMove(self):
        return self.isFirstMove
    
    def logMove(self):
        self.isFirstMove = False

    def isCorrectMove(self, s):
        if (s.lower() == "reveal"):
            return True
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

        if (isCorrectCard(s[1]) and isCorrectCard(s[2])):
            return True
        return False

    def updateHand(self, newHand):
        self.currHand = newHand
        self.currPlayer += 1
        if self.currPlayer == len(self.alivePlayers):
            self.currPlayer = 0
        self.callToMove(self.id[self.currPlayer])
    
    def addCardToPlayer(self, id):
        self.isLooser[id] = 1
        self.numberOfCards[id] += 1
        self.numberOfCardsInGame += 1
        if self.numberOfCards[id] > 5:
            self.alivePlayers.remove(id)
            isJoined[id] = 0
            self.numberOfCardsInGame -= 6

    def checkCntOf(self, rang, count):
        if self.cntOfCardsByRang.get(rang) == None:
            return 0
        return self.cntOfCardsByRang.get(rang) >= count

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
            if self.currHand[1] < 4:
                res = False
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
            if self.currHand[1] < 4:
                res = False
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
        for curId in self.alivePlayers:
            res += self.getName(curId) + ": "
            for i in range(self.numberOfCards[curId]):
                res = self.addCardToString(res, self.cardDeck[curPos], (i == 0))
                curPos += 1
            res += "\n"
        self.printOut(res)

    def started(self):
        return self.isStarted

    def finish(self):
        isJoined[self.alivePlayers[0]] = 0
        self.printOut('The winner is ' + self.getLinkedName(self.id[0])) 

    def finishRound(self):
        self.reveal()
        prevPlayer = self.currPlayer - 1
        if prevPlayer < 0:
            prevPlayer += len(self.alivePlayers)

        if self.hasHand():
            self.addCardToPlayer(self.id[self.currPlayer])
        else:
            self.addCardToPlayer(self.id[prevPlayer])
        self.currHand = [-1, -1, -1]
        self.printNumberOfCards()

    def getChat(self, chatId):
        self.chat_id = chatId

    def cancel(self):
        for curId in self.id:
            isJoined[curId] = 0
    

def registerPlayer(user):
    if user.first_name == None:
        firstNameById[user.id] = ''       
    else:
        firstNameById[user.id] = user.first_name
        
    if user.last_name == None:
        lastNameById[user.id] = ''
    else:
        lastNameById[user.id] = user.last_name

def registerChat(id):
    if gamesByChatId.get(id) == None:
        gamesByChatId[id] = Game()
        gamesByChatId[id].getChat(id)

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
    if curGame.isCreated and not curGame.isStarted:
        curGame.cancel()
        bot.delete_message(curGame.chat_id, curGame.message_id)
        gamesByChatId[message.chat.id] = None
        bot.send_message(message.chat.id, "Successfully canceled")

@bot.message_handler(commands=['help'])
def getRules(message):
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

@bot.message_handler(commands=['hands'])
def getHelp(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    helplist = 'Suits:\n'
    helplist += '0 - ' + cardSuits[0] + '\n' + '1 - ' + cardSuits[1] + '\n'
    helplist += '2 - ' + cardSuits[2] + '\n' + '3 - ' + cardSuits[3] + '\n'
    helplist += 'Hands in in ascending order:\n'
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
    callback_button = types.InlineKeyboardButton(text="Join", callback_data="Join")
    keyboard.add(callback_button)
    gamesByChatId[message.chat.id].createGame(message, keyboard)
   
@bot.callback_query_handler(func=lambda c: True)
def inline(c):
    if c.data == 'Join':
        registerPlayer(c.from_user)
        gamesByChatId[c.message.chat.id].addPlayer(c.message, c.from_user) 

@bot.message_handler(commands=['leavegame'])
def leavegame(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    gamesByChatId[message.chat.id].removePlayer(message) 

@bot.message_handler(commands=['countcards'])
def countcards(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    gamesByChatId[message.chat.id].printNumberOfCards()

@bot.message_handler(commands=['startgame'])
def startgame(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    gamesByChatId[message.chat.id].start(message)

@bot.message_handler(commands=['r'])
def getmsg(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    global gamesByChatId
    curGame = gamesByChatId[message.chat.id]
    if (not curGame.isCreated or not curGame.isStarted):
        return
    if (message.from_user.id != curGame.id[curGame.currPlayer]):
        return
    if curGame.firstMove():
        curGame.printOut("You can't reveal at the first move")
    else:
        curGame.finishRound()
        if len(curGame.alivePlayers) == 1:
            curGame.finish()
            curGame = None
        else:
            curGame.startRound()
    gamesByChatId[message.chat.id] = curGame

@bot.message_handler(commands=['m'])
def getmessage(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    global gamesByChatId
    curGame = gamesByChatId[message.chat.id]
    curText = message.text[3:]
    if (not curGame.isStarted):
        return 
    if (message.from_user.id != curGame.id[curGame.currPlayer]):
        return
    if curGame.isCorrectMove(curText) and curGame.started():
        if not curGame.isHigherHand(curGame.parseStringToHand(curText)):
            curGame.printOut("It's a not higher than current")
        else:                
            curGame.updateHand(curGame.parseStringToHand(curText))
        curGame.logMove()
    else: 
        if curGame.isStarted:
            curGame.printOut("Incorrect move")
    gamesByChatId[message.chat.id] = curGame


@bot.message_handler(content_types=['text'])
def getm(message):
    registerChat(message.chat.id)
    registerPlayer(message.from_user)
    if (message.text == "go"):
        bot.send_message(message.chat.id, "successfully")
        chatsById[message.from_user.id] = message.chat.id

bot.polling()
