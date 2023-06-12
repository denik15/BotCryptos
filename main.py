import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import time


# URL для парсингу курсу валют
def get_crypto_cource():
    url = f"https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
    response = requests.get(url)
    data = response.json()

    result = []
    for i in data:
        result.append((i['txt'], i['rate']))

    return result

get_cource = get_crypto_cource()

# URL для парсингу цін криптовалют
def get_crypto_price(crypto_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    print(data)
    return data[crypto_id]['usd']


bitcoin_price = get_crypto_price('bitcoin')
ethereum_price = get_crypto_price('ethereum')
litecoin_price = get_crypto_price('litecoin')

def get_exchange_rate(currency):
    url = f'/{currency}'  
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    rate = soup.find('span', class_='rate').text.strip()
    return rate


def update_prices(context: CallbackContext) -> None:
    usd_rate = get_exchange_rate('usd')
    euro_rate = get_exchange_rate('euro')
    context.bot_data['usd_rate'] = usd_rate
    context.bot_data['euro_rate'] = euro_rate

    bitcoin_price = get_crypto_price('bitcoin')
    litecoin_price = get_crypto_price('litecoin')
    etherium_price = get_crypto_price('etherium')
    context.bot_data['bitcoin_price'] = bitcoin_price
    context.bot_data['litecoin_price'] = litecoin_price
    context.bot_data['etherium_price'] = etherium_price


def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Крипта", callback_data='crypto')],
        [InlineKeyboardButton("Курси валют", callback_data='exchange')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Оберіть опцію:', reply_markup=reply_markup)


def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()  
    

    if query.data == 'crypto':
        keyboard = [
            [InlineKeyboardButton("Bitcoin", callback_data='bitcoin')],
            [InlineKeyboardButton("Litecoin", callback_data='litecoin')],
            [InlineKeyboardButton("Etherium", callback_data='etherium')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text('Оберіть криптовалюту:', reply_markup=reply_markup)

    elif query.data == 'bitcoin':
        price = context.bot_data.get('bitcoin_price', f'${bitcoin_price}')
        query.message.reply_text(f'Ціна Bitcoin: {price}')

    elif query.data == 'litecoin':
        price = context.bot_data.get('litecoin_price', f'${litecoin_price}')
        query.message.reply_text(f'Ціна Litecoin: {price}')


    elif query.data == 'etherium':
        price = context.bot_data.get('etherium_price', f'${ethereum_price}')
        query.message.reply_text(f'Ціна Etherium: {price}')


    elif query.data == 'exchange': 

        keyboard = []

        global lst_p
        lst_p = []
        for pair in get_cource:   
            lst_p.append(pair)
            keyboard.append([InlineKeyboardButton(pair[0], callback_data=str(pair[0]))])


        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text('Оберіть валюту:', reply_markup=reply_markup)

    for i in lst_p:
        if query.data == str(i[0]):
            cource = context.bot_data.get(i[1], i[1])
            query.message.reply_text(f'Курс: {cource}')


def main() -> None:
    updater = Updater("YOUR_TOKE")  
    job_queue = updater.job_queue

    job_queue.run_repeating(update_prices, interval=3600, first=0)

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button_click))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()