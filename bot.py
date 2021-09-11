import telebot
from conf import tok
import database, location

bot = telebot.TeleBot(tok)

@bot.message_handler(commands=['start'])
def handle_start(message):
    """
    Initial message.
    Registers a new user if they are not registered.
    """
    bot.send_message(message.chat.id, "Вітаю! Я бот для пошуку тварин у Львові.\n\
Разом ми зможемо допомогати господарам знаходити їхніх втрачених тваринок.")
    # bot.send_location(chat_id, lat, lon)
    username = message.from_user.username
    if database.is_new_user(username):
        bot.reply_to(message, "Уведіть адресу свого будинку, будь ласка.")
        bot.register_next_step_handler(message, address)


def address(message):
    addr = message.text
    coord = location.find_house_coordinates(addr)
    if coord:
        database.add_user(message.from_user.username, coord[0], coord[1])
        bot.send_message(message.chat.id, "Дякуємо! Ви успішно зареєструвались.")
    else:
        bot.send_message(message.chat.id, "Вибачте, введенна адреса не знайдена.\nСпробуйте, будь ласка, ще раз.")


def handle_reply(message):
    bot.reply_to(message, message + ' Thanks')


@bot.message_handler(commands=['message'])
def handle_message(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    buttonA = telebot.types.KeyboardButton('A')
    buttonB = telebot.types.KeyboardButton('B')
    buttonC = telebot.types.KeyboardButton('C')

    markup.row(buttonA, buttonB, buttonC)

    bot.send_message(message.chat.id, 'It works!', reply_markup=markup)

bot.polling()