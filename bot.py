import os, logging
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
from selenium import webdriver
from datetime import date, datetime
from pymongo import MongoClient

# Enable logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Load environment variables from ".emv" file
load_dotenv()
TOKEN = os.environ.get('TELEGRAM-BOT-TOKEN')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

# Connect to MongoDB Atlas
client = MongoClient(f'mongodb+srv://{DB_USER}:{DB_PASSWORD}@cluster0.4fi93.mongodb.net/toto_db?retryWrites=true&w=majority')
db = client.toto_db
draws = db.draws
# draw = {
#     '_id': 'next_draw',
#     'date': '2021-01-01',
#     'date_string': 'Fri, 01 Jan 2021, 6.30pm',
#     'jackpot': '$1,000,000 est'
# }
# draw_id = draws.insert_one(draw)
print(draws.find_one({
    '_id': 'next_draw'
}))

# Verify if token is correct
def verify_bot() -> None:
    bot = Bot(token=TOKEN)
    print(bot.get_me())

# '/start' handler
def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Hello! Use /nextdraw to get details of the upcoming Toto draw.')

# '/nextdraw' handler
def next_draw(update: Update, _: CallbackContext) -> None:
    date, jackpot = get_next_draw_date_and_jackpot()
    update.message.reply_text(f'Date: {date}\nJackpot: {jackpot}')

# Handler for unknown commands
def unknown(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Sorry, don\'t understand.')

# Retrieve upcoming draw date and jackpot
def get_next_draw_date_and_jackpot() -> (str, str):
    URL = 'https://www.singaporepools.com.sg/en/product/pages/toto_results.aspx'
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--incognito')
    driver = webdriver.Chrome(options=options) # Place chromedriver.exe in the same directory as this .py file
    driver.get(URL)
    jackpot_elem = driver.find_element_by_xpath("//span[@style='color:#EC243D; font-weight:bold']")
    draw_date_elem = driver.find_element_by_class_name('toto-draw-date')
    next_draw_date_string = draw_date_elem.text
    next_draw_jackpot = jackpot_elem.text
    driver.quit()
    logging.info(f'Web Scrape Results | Next Draw Date: {next_draw_date_string} | Jackpot: {next_draw_jackpot}')
    return next_draw_date_string, next_draw_jackpot

# next_draw_date = date(2021, 1, 1)
# next_draw_date_string = 'Fri, 01 Jan 2021, 6.30pm'
# next_draw_jackpot = '$1,000,000 est'

# def get_next_draw_date_and_jackpot() -> (str, str):
#     today_date = date.today()
#     logging.info(f'Today\'s Date: {today_date} | Next Draw Date: {next_draw_date}')
#     if today_date > next_draw_date:
#         web_scrape_and_update()
#     return next_draw_date_string, next_draw_jackpot

# def web_scrape_and_update() -> None:
#     URL = 'https://www.singaporepools.com.sg/en/product/pages/toto_results.aspx'
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')
#     options.add_argument('--incognito')
#     driver = webdriver.Chrome(options=options) # Place chromedriver.exe in the same directory as this .py file
#     driver.get(URL)
#     jackpot_elem = driver.find_element_by_xpath("//span[@style='color:#EC243D; font-weight:bold']")
#     draw_date_elem = driver.find_element_by_class_name('toto-draw-date')
#     next_draw_date_string = draw_date_elem.text
#     next_draw_jackpot = jackpot_elem.text
#     driver.quit()
#     next_draw_date = convert_to_date(next_draw_date_string)
#     logging.info(f'After Update | Next Draw Date: {next_draw_date_string} | Jackpot: {next_draw_jackpot}')

# def convert_to_date(date_string: str) -> date:
#     draw_datetime = datetime.strptime(date_string, '%a, %d %b %Y , %I.%M%p')
#     return draw_datetime.date()

# Function to start to bot
def main() -> None:
    verify_bot()

    updater = Updater(token=TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('nextdraw', next_draw))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()

    updater.idle()

# Start the bot
# main()
