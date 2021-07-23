# -*- coding: utf-8 -*-
import json
import time

import requests
import os
from bs4 import BeautifulSoup as bs
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot
from dotenv import load_dotenv


load_dotenv()

# Bot token
token = os.getenv('token')
# Dictionary with all users and urls associated
users = {}
#Init bot for sending messages
bot = Bot(token=token)

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Utilitza la comanda /subscribe seguida de una o mes urls de decathlon, el bot tavisara quan hi hagui stock. Si vols parar de rebre notificacions, /unsubscribe')


def help(update, context):
    """Send a message when the command /help is issued."""

    update.message.reply_text('Help!')


def subscribe(update, context):
    if len(context.args) == 0:
        update.message.reply_text("You have to put one or more links")
        return

    add_user(update.message, context.args)

    print("Adding user " + str(update.message.chat_id) + " with args " + " ".join(context.args))


def unsubscribe(update, context):
    print("User " + str(update.message.chat_id) + " removed")
    remove_user(update.message.chat_id)
    update.message.reply_text("Canceled subscriptions")


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    print('Update ' + update + ' caused error ')


def init_dict():
    global users
    try:
        with open("users.json", "r") as read_file:
            users = json.load(read_file)
            pass
    except:
        open("users.json", "x")


def write_dict():
    with open('users.json', 'w') as outfile:
        json.dump(users, outfile)


def add_user(user_id, urls):
    user_id = user_id.chat_id
    if str(user_id) not in users or len(users[str(user_id)]) == 0:
        users[str(user_id)] = (" ".join(urls), 0)
        bot.send_message(chat_id=user_id, text="You will be notified when there is stock of the product")
    else:
        bot.send_message(chat_id=user_id, text="You already have a subscription, unsubscribe to add another")
    write_dict()


def remove_user(user_id):
    if str(user_id) in users:
        del users[str(user_id)]
        write_dict()


def check_stock():
    global bike_instances
    request = requests.get("https://www.canyon.com/en-es/outlet-bikes/mountain-bikes/")
    soup = bs(request.content, features="html.parser")
    for user_id, bike_list in users.items():
        if len(bike_list) != 0:
            bike = bike_list[0]
            old_instances = bike_list[1]
            new_instances = soup.text.count(bike)
            if new_instances != old_instances:
                bike_list = (bike, new_instances)
                bot.send_message(chat_id=user_id, text="There are new " + bike + " in stock")


def start_bot():
    """Start the bot."""
    #Init updater with bots token
    updater = Updater(token, use_context=True)

    print("Bot started")
    init_dict()

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("subscribe", subscribe, pass_args=True))
    dp.add_handler(CommandHandler("unsubscribe", unsubscribe))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.


if __name__ == '__main__':
    start_bot()
    bike_instances = 0
    while True:
        print('Checking stock')
        check_stock()
        time.sleep(900)