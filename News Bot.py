#!/usr/bin/python
# -*- coding: utf-8 -*-
# i have been tasked to comment this shambolic code.

# random imports

from newsapi import NewsApiClient
import json
import random
from time import sleep
import telebot
import schedule
from threading import Thread
from datetime import date, timedelta
import os
import sys

# global variables as the functions may need to modify them

global bot
global TOKEN
global newsapi

# Init

# there is no need to change these API keys. Each key supports 100 calls and the code randomly rotates among 3 keys when calling

newsapiList = ['fd95ae3de99a41b79fd5398cdd40e9a0',
               '13cdfd92fd2f4dc78583334fb713caa9',
               'd6603f6ab89a4b6eb81ab0a2e43fb12d']

newsapi = NewsApiClient(api_key='fd95ae3de99a41b79fd5398cdd40e9a0')  # THIS IS THE FIRST NEWSAPI KEY (more below)

# 13cdfd92fd2f4dc78583334fb713caa9
# d6603f6ab89a4b6eb81ab0a2e43fb12d

# this API key is tagged to my own Telegram account. As such, only I have access to the bot's setting via @BotFather
# If needed, change this to a new Telegram API key, and follow the documentation to set up the bot's cosmetic details.

bot_token = ''  # Insert Telegram API key here
bot_user_name = '' # Insert Telegram Bot username here (should be in the format "my_news_bot)

TOKEN = bot_token
bot = telebot.TeleBot(TOKEN)

# The JSON file contains all registered chat IDs and their selected keywords. This allows the bot to retain information when it automatically shuts down

try:
    with open('data.json') as json_file:
        active = json.load(json_file)
except:
    active = {}


def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)


def send_daily():
    global active
    global response

    for i in active.keys():
        response = get_Articles(active[i])
        articleCount = len(response['articles'])
        if articleCount < 3:
            max = articleCount
        else:
            max = 3
        for j in range(max):

            articleTitle = response['articles'][j]['title']
            articleLink = response['articles'][j]['url']

            bot_message = "<a href='" + articleLink + "'>" \
                + articleTitle + '</a>'

            bot.send_message(i, bot_message, parse_mode='HTML')
    return schedule.CancelJob


def get_Articles(keywords='None'):
    global newsapi
    newsapi = NewsApiClient(api_key=newsapiList[random.randint(0, 2)])
    if keywords == 'None':
        top_headlines = newsapi.get_top_headlines(language='en',
                page_size=100)
    else:
        top_headlines = newsapi.get_top_headlines(language='en',
                page_size=100, q=keywords)
        if len(top_headlines['articles']) == 0:
            top_headlines = newsapi.get_top_headlines(language='en',
                    page_size=100)
    temp = json.dumps(top_headlines)
    response = json.loads(temp)
    return response


@bot.message_handler(commands=['start'])
def start_command(message):
    global response
    global active
    response = get_Articles()
    if message.chat.id in active.keys():
        bot.send_message(message.chat.id,
                         'Bot has already been intialised.')
        return
    else:

        bot.send_message(message.chat.id,
                         'Bot intialised! You will now begin to receive news articles every 24 hours.'
                         )
        active[message.chat.id] = 'None'
        with open('data.json', 'w') as convert_file:
            convert_file.write(json.dumps(active))
        bot.send_message(message.chat.id,
                         'You may run the command /option [keyword] to fine tune what articles you wish to receive!\nFor example: /option Russia'
                         )


@bot.message_handler(commands=['unsub'])
def unsub_command(message):
    if message.chat.id in active.keys():
        active.pop(message.chat.id)
        bot.send_message(message.chat.id,
                         'You have opted out of receiving daily articles.'
                         )
        with open('data.json', 'w') as convert_file:
            convert_file.write(json.dumps(active))
        return
    else:

        bot.send_message(message.chat.id,
                         'You have not opted in to receive daily articles yet! Use /start to do so.'
                         )


@bot.message_handler(commands=['option'])
def set_option(message):
    param = message.text
    param = param.replace('/option ', '')

    if param == '/option':
        bot.send_message(message.chat.id, 'The current keyword set is: '
                          + active[message.chat.id])
        return

    active[message.chat.id] = param
    bot.send_message(message.chat.id,
                     "Your daily news will now prioritise articles containing '"
                      + param + "'.")
    with open('data.json', 'w') as convert_file:
        convert_file.write(json.dumps(active))


@bot.message_handler(commands=['daily'])
def daily_command(message):
    bot.send_message(message.chat.id,
                     'Forcing a refresh of news articles... Please be patient!'
                     )
    global response
    response = get_Articles(active[message.chat.id])
    articleCount = len(response['articles'])

    if articleCount < 3:
        param = articleCount
    else:
        param = 3

    for i in range(param):

        articleTitle = response['articles'][i]['title']
        articleLink = response['articles'][i]['url']

        bot_message = "<a href='" + articleLink + "'>" + articleTitle \
            + '</a>'


        bot.send_message(message.chat.id, bot_message, parse_mode='HTML'
                         )


@bot.message_handler(commands=['help'])
def message_command(message):
    bot.send_message(message.chat.id,
                     '''Greetings! I am a scuffed bot created by a washed up programmer. Here are the commands that he was able to cram in: 
/start : Initialises the bot and allows it to automatically send news articles every 24 hours. There is no need to run this more than once.
/help : Shows this menu of available commands
/option [keyword] : Set a keyword that the bot will look for when sending daily news.
/news [number of articles] : Gets more articles from the top headlines of the past day. The number of article field is optional.
/search [search term] : Searches for articles containing the keyword.
/daily : Forces refresh of the news articles for the day and sends 3 articles.
/status : Checks status of bot and number of registered chats.''')


@bot.message_handler(commands=['creator'])
def creator_command(message):
    bot.send_message(message.chat.id,
                     'This bot is made by the 09/23 DIS Wing Learning Committee! For clarifications on the bot, you may contact Che Khai at 94762447.'
                     )


@bot.message_handler(commands=['news'])
def get_news(message):
    response = get_Articles()
    articleCount = len(response['articles'])
    param = message.text
    param = param.replace('/news ', '')

    try:
        param = int(param)
    except:
        param = 3

    for i in range(param):

        randomNo = random.randint(0, articleCount - 1)
        articleTitle = response['articles'][randomNo]['title']
        articleLink = response['articles'][randomNo]['url']

        bot_message = "<a href='" + articleLink + "'>" + articleTitle \
            + '</a>'

        bot.send_message(message.chat.id, bot_message, parse_mode='HTML'
                         )


@bot.message_handler(commands=['search'])
def search_news(message):
    global response
    search = message.text
    search = search.replace('/search ', '')
    today = date.today()
    weekAgo = today - timedelta(days=7)

    if search == '/search':
        bot.send_message(message.chat.id, 'No search query detected.')
        return

    search_headlines = newsapi.get_everything(language='en', q=search,
            from_param=str(weekAgo), to=str(today), sort_by='relevancy')
    temp = json.dumps(search_headlines)
    searchArticles = json.loads(temp)
    articleCount = len(searchArticles['articles'])

    if articleCount == 0:
        bot.send_message(message.chat.id,
                         'No articles found within the past week.')
        return


    for i in range(3):

        randomNo = random.randint(1, articleCount - 1)
        articleTitle = searchArticles['articles'][randomNo]['title']

        articleLink = searchArticles['articles'][randomNo]['url']
        bot_message = "<a href='" + articleLink + "'>" + articleTitle \
            + '</a>'
        bot.send_message(message.chat.id, bot_message, parse_mode='HTML'
                         )


def send_articles(articles, chat_id):

    articleCount = len(articles['articles'])
    param = 2

    for i in range(param):

        randomNo = random.randint(0, articleCount - 1)
        articleTitle = articles['articles'][randomNo]['title']
        articleLink = articles['articles'][randomNo]['url']

        bot_message = "<a href='" + articleLink + "'>" + articleTitle \
            + '</a>'

        bot.send_message(chat_id, bot_message, parse_mode='HTML')


@bot.message_handler(commands=['status'])
def status_command(message):
    botMessage = 'The bot is alive! There are currently ' \
        + str(len(active)) + ' registered chats.'
    bot.send_message(message.chat.id, botMessage)

print ('Bot is up and running!')

if __name__ == '__main__':
    schedule.every().day.at('10:00').do(send_daily)  # 10:00 = 6pm

    Thread(target=schedule_checker).start()
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except (ConnectionError, ReadTimeout) as e:
        sys.stdout.flush()
        os.execv(sys.argv[0], sys.argv)
    else:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
