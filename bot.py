import telebot
# import animals
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
    user = message.from_user.username
    '''
    if user not in animals:
        bot.send_message(message.chat.id, "Уведіть свою адресу, будь ласка.")
    '''
    bot.reply_to(message, "Уведіть свою адресу, будь ласка.")
    bot.register_next_step_handler(message, address)


def address(message):
    addr = message.text
    '''
    add addr to db
    '''

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