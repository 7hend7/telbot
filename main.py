import os
import re
import requests
import telebot  # pyTelegramBotAPI package https://pytba.readthedocs.io/en/latest/quick_start.html
from telebot.types import InputFile
import pathlib

URL = "https://api.coingecko.com/api/v3/simple/price?ids="
URL_PARAMS = "&vs_currencies="
TOKEN = "7804944199:AAGt6x6IB9SfMtr0Q2Zjm8nGTD9rzCW8Seg"
# folder's name
LOGO_FOLDER  = "coins_logo"
LOGO_PATH = pathlib.Path(__file__).resolve().parent / LOGO_FOLDER

COINS = ("bitcoin", "ethereum", "dogecoin", "tether")

bot = telebot.TeleBot(TOKEN)


# get coins rate throught API
def get_coin_course(
    coins: tuple = COINS, curr: str = "usd"
) -> dict:

    responce = requests.get(URL + ",".join(coins) + URL_PARAMS + curr)
    data = responce.json()
    return data


# calculate count of coins that could be bought
def create_assets_msg(data: dict, assets: float) -> str:

    result = "You can bought: \n"
    for coin, curse in data.items():
        for value in curse.values():
            result += coin.capitalize() + " : " + str(assets / value) + "\n"
    return result


# send logo of coins with rate as caption
def send_coin_course(data: dict, chat_id: int):
    # generate path for coin image
    def gen_logo_paths():
        files = pathlib.Path(LOGO_PATH).glob("*")
        for filename in files:
            yield os.path.join(LOGO_PATH, filename)

    # generate string for coin rate
    def gen_coin_course():
        for coin, curse in data.items():
            for curr, value in curse.items():
                yield coin + ": " + str(value) + " " + curr.upper()

    # send image with coin rate caption
    coin_courses = gen_coin_course()
    for course in coin_courses:
        logo_paths = gen_logo_paths()
        for lpath in logo_paths:
            # split string to get coin name
            # if coin name is the part of the file name try to send
            if course.split(":")[0] in lpath:
                bot.send_photo(chat_id, InputFile(pathlib.Path(lpath)), caption=course)
                break
        else:
            # send default logo if coin's logo doesn't exist in the logo folder
            bot.send_photo(
                chat_id,
                InputFile(pathlib.Path(os.path.join(LOGO_PATH, "default-logo.png"))),
                caption=course,
            )


@bot.message_handler(commands=["start", "all"])
def start(message):

    data = get_coin_course()
    send_coin_course(data, message.chat.id)
    bot.send_message(message.chat.id, "Enter your USD assets:")

# TODO!
@bot.message_handler(regexp=r"(\w+)\s(\d+)")
def calc_purchase_coin(message):
    mess = re.search(r"(?P<coin>\w+)\s(?P<money>\d+)", message.text)


    bot.send_message(message.chat.id, mess.groupdict()['coin'] + mess.groupdict()['money'])


@bot.message_handler(regexp=r"^\d+\.?\,?\d?\d?")  # content_types=["text"]
def calc_purchase_coins(message):

    assets = message.text
    data = get_coin_course()
    try:
        assets = float(assets.replace(",", "."))
        assets_msg = create_assets_msg(data=data, assets=assets)
        bot.send_message(message.chat.id, assets_msg)
    except Exception as e:
        bot.send_message(message.chat.id, "Error: " + str(e) + " Is it valid number?")


if __name__ == "__main__":

    bot.infinity_polling()
