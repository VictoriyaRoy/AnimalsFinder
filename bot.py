import telebot
import user
from conf import tok

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
    if user.is_new_user(username):
        bot.reply_to(message, "Уведіть адресу свого будинку, будь ласка.")
        bot.register_next_step_handler(message, address)


def address(message):
    addr = message.text
    # There will be convertion address to coordinates
    user.add_user(message.from_user.username, 0, 0)
    bot.send_message(message.chat.id, "Дякуємо! Ви успішно зареєструвались.")

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