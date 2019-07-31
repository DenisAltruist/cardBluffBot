FROM python:3-alpine

WORKDIR /usr/src/app

RUN pip install --no-cache-dir telebot pytelegrambotapi cherrypy

COPY . .

CMD [ "python", "./bot.py" ]