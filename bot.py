import os, logging
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
from selenium import webdriver

# Enable logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Load environment variables
load_dotenv()
TOKEN = os.environ.get('TELEGRAM-BOT-TOKEN')

# Verify if token is correct
bot = Bot(token=TOKEN)
print(bot.get_me())

# '/start' handler
def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Hello! Use /nextdraw to get details of the upcoming Toto draw.')

# '/nextdraw' handler
def next_draw(update: Update, _: CallbackContext) -> None:
    date, jackpot = get_next_draw_date_and_jackpot()
    update.message.reply_text(f'Date: {date}\nJackpot: {jackpot}')

# Unknown handler
def unknown(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Sorry, don\'t understand.')

def get_next_draw_date_and_jackpot() -> (str, str):
  URL = 'https://www.singaporepools.com.sg/en/product/pages/toto_results.aspx'
  options = webdriver.ChromeOptions()
  options.add_argument('--headless')
  options.add_argument('--incognito')
  driver = webdriver.Chrome(options=options) # Place chromedriver.exe in the same directory as this .py file
  driver.get(URL)
  jackpot_elem = driver.find_element_by_xpath("//span[@style='color:#EC243D; font-weight:bold']")
  draw_date_elem = driver.find_element_by_class_name('toto-draw-date')
  date = draw_date_elem.text
  jackpot = jackpot_elem.text
  driver.quit()
  logging.info(f'Date: {date}')
  logging.info(f'Jackpot: {jackpot}')
  return date, jackpot

# Function to start to bot
def main() -> None:
    updater = Updater(token=TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("nextdraw", next_draw))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()

    updater.idle()

# Start the bot
main()
