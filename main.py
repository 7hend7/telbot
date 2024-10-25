import requests
import telebot
from decimal import Decimal


URL = "https://api.coingecko.com/api/v3/simple/price?ids="
URL_PARAMS = "&vs_currencies="
TOKEN = '7804944199:AAGt6x6IB9SfMtr0Q2Zjm8nGTD9rzCW8Seg'

bot = telebot.TeleBot(TOKEN)


def get_coin_course(coins:tuple=('bitcoin','ethereum','tether'), curr:str='usd') -> dict:

    responce = requests.get(URL + ','.join(coins) + URL_PARAMS + curr)
    data = responce.json()
    return data


def create_course_msg(data: dict) -> str:

    msg = 'Coins course for now: \n'
    for coin, curse in data.items():
        for curr, value in curse.items():
            msg += coin.capitalize() + ': ' + str(value) + ' ' + curr + ' | \n'
    return msg


def create_assets_msg(data:dict, assets:float) -> str:

    result = 'You can bought: \n'
    for coin, curse in data.items():
        for value in curse.values():
            result += coin.capitalize() + ' : ' + str(assets/value) + '\n'  
    return result

    
@bot.message_handler(commands=['start'])
def start(message):
    data = get_coin_course()
    msg = create_course_msg(data)
    bot.send_message(message.chat.id, msg)
    bot.send_message(message.chat.id, 'Enter your USD assets:')


@bot.message_handler(content_types=["text"])
def calculate_bought(message):

    assets = message.text
    data = get_coin_course()
    try:
        assets = float(assets.replace(',', '.'))
        assets_msg = create_assets_msg(data=data, assets=assets)
        bot.send_message(message.chat.id,  assets_msg)
    except Exception as e:
        bot.send_message(message.chat.id, 'Error: ' + str(e) + ' Is it valid number?')


if __name__ == '__main__':
    bot.infinity_polling()
