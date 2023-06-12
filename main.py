import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler


def get_all_cryptos():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",  # Specify the desired currency
        "order": "market_cap_desc",
        "per_page": 100,  # Adjust the number of results per page as needed
        "page": 1
    }

    response = requests.get(url, params=params)
    data = response.json()

    list_crypts = []
    for crypto in data:
        list_crypts.append((crypto['name'], crypto['symbol'], crypto['current_price']))

    return list_crypts

get_cryptos = get_all_cryptos()


# URL for parsing cource валют
def get_crypto_cource():
    url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
    response = requests.get(url)
    data = response.json()

    result = []
    for i in data:
        result.append((i['txt'], i['rate']))

    return result

get_cource = get_crypto_cource()


# URL for parsing coint crypto
def get_crypto_price(crypto_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    print(data)
    return data[crypto_id]['usd']


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
        # list keyboards crypto
        keyboard = []

        # list crypto
        global lst_crypto
        lst_crypto = []

        # add keyboards
        for crypto in get_cryptos:   
            lst_crypto.append(crypto)
            keyboard.append([InlineKeyboardButton(crypto[0], callback_data=str(crypto[0]))])

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text('Оберіть криптовалюту:', reply_markup=reply_markup)


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

    #FIXME
    for i in lst_crypto:
        if query.data == [str(c[0]) for c in lst_crypto]:
            price = context.bot_data.get(i[1], i[1])
            query.message.reply_text(f'Ціна: {price}')


def main() -> None:
    updater = Updater("6096869497:AAFdCF3r3bQMZdI8ZRxnyEAn3-vc_bBsIpc")  
    job_queue = updater.job_queue

    job_queue.run_repeating(update_prices, interval=10, first=0)

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button_click))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()