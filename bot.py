import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.environ.get('TELEGRAM-BOT-TOKEN')

import telegram
bot = telegram.Bot(token=TOKEN)

print(bot.get_me()) # verify if token is correct

from telegram.ext import Updater
updater = Updater(token=TOKEN)

dispatcher = updater.dispatcher

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

### "/start" command handler ###

def start(update, context):
  context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

### Message handler ###

def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

from telegram.ext import MessageHandler, Filters
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
