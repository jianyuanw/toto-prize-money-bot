import os, logging, re
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
#     'date': 'Mon, 19 Apr 2021 , 6.30pm',
#     'jackpot': '$4,000,000 est'
# }
# result = draws.insert_one(draw)
# print(result)
# draw = draws.find_one({ '_id': 'next_draw' })
# draw_date = draw['date']
# for elem in draw_date.split():
#     print(elem.strip(','))

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
    # Get document from db
    # Compare with today's date
    # If not yet pass, return details from document
    # Else web scrape and return details from results
    URL = 'https://www.singaporepools.com.sg/en/product/pages/toto_results.aspx'
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--incognito')
    driver = webdriver.Chrome(options=options) # Place chromedriver.exe in the same directory as this .py file
    driver.get(URL)
    jackpot_elem = driver.find_element_by_xpath("//span[@style='color:#EC243D; font-weight:bold']")
    date_elem = driver.find_element_by_class_name('toto-draw-date')
    date_string = date_elem.text
    jackpot = jackpot_elem.text
    driver.quit()
    logging.info(f'Scraping Singapore Pools website... | Next Draw Date: {date_string} | Jackpot: {jackpot}')
    return date_string, jackpot

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

def convert_to_date(date_string: str) -> date:
    year = re.search('\d{4}', date_string).group()
    month = re.findall('\w{3}', date_string)[1]
    day = re.search('\d{2}', date_string).group()
    return datetime.strptime(f'{year}{month}{day}', '%Y%b%d').date()

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
