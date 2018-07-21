# -*- coding: utf-8 -*-
TOKEN = '572605462:AAHJZFgDkRilYhxmOYGTIPX5iA12VZ262PI'
MAX_NUMBER_OF_PLAYERS = 8

WEBHOOK_HOST = '207.154.227.181' 
WEBHOOK_PORT = 443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше

WEBHOOK_SSL_CERT = './cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './private.key'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % TOKEN




