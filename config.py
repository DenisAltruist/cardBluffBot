import os

# -*- coding: utf-8 -*-
TOKEN = os.environ['TOKEN']
MAX_NUMBER_OF_PLAYERS = 10
MIN_NUMBER_OF_PLAYERS = 2
MIN_NUMBER_OF_ROUNDS = 3 #Were started
TIME_TO_MOVE = 60
MIN_RESPONSE_TIME_DELTA = 5
MAX_QUERY_LIMIT_PER_USER = 6
GOOD_TIME_INACTIVITY = 10
TIME_TO_START_GAME = 1000

WEBHOOK_HOST = os.environ['HOST']
WEBHOOK_PORT = 80  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше

WEBHOOK_SSL_CERT = './cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './private.key'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "http://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % TOKEN