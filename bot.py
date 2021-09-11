import telebot
import telebot_calendar
import datetime
from telebot_calendar import Calendar, CallbackData
# import animals
from conf import tok

bot = telebot.TeleBot(tok)

calendar = Calendar()
calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")
now = datetime.datetime.now()


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
        bot.register_next_step_handler(message, address)
    '''


def address(message):
    addr = message.text
    '''
    add addr to db
    '''


@bot.message_handler(commands=['lost'])
def handle_lost(message):
    """
    Handles the lost animal.
    Helps the owner find their animal.
    """
    keyboard = telebot.types.InlineKeyboardMarkup()
    animal_types = ['Кіт', 'Собака', 'Інше']
    for anim_type in animal_types:
        keyboard.row(telebot.types.InlineKeyboardButton(anim_type, callback_data=f'type: {anim_type}'))
    bot.send_message(message.chat.id, 'Яка тварина у вас загубилася?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('type'))
def an_type_callback(query):
    data = query.data
    if data[6:] == 'Інше':
        bot.send_message(query.from_user.id, "Уточніть, яка тварина у вас загубилася, будь ласка.")
        bot.register_next_step_handler_by_chat_id(query.from_user.id, get_animal_type)
    elif data[6:] in ('Кіт', 'Собака'):
        with open('lost.txt', 'w', encoding='utf-8') as lost_an_f:
            lost_an_f.write(data[6:] + '\n')
        # lost = data[6:]
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton('Ч', callback_data='sex: Ч'))
        keyboard.row(telebot.types.InlineKeyboardButton('Ж', callback_data='sex: Ж'))
        bot.send_message(query.from_user.id, 'Якої статі ваша тварина?', reply_markup=keyboard)
        # bot.send_message(query.from_user.id, "Якої статі ваша тварина?")
        # bot.register_next_step_handler_by_chat_id(query.from_user.id, get_animal_sex)
    # elif data in ('Ч', 'Ж'):
    #     lost_sex = data
    #     bot.send_message(query.from_user.id, f"ви загубили {lost} {lost_sex}")


def get_animal_type(message):
    anim_type = message.text
    with open('lost.txt', 'w', encoding='utf-8') as lost_an_f:
        lost_an_f.write(anim_type + '\n')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton('Ч', callback_data='sex: Ч'))
    keyboard.row(telebot.types.InlineKeyboardButton('Ж', callback_data='sex: Ж'))
    bot.send_message(message.chat.id, 'Якої статі ваша тварина?', reply_markup=keyboard)
    # bot.register_next_step_handler(message, get_animal_sex)


@bot.callback_query_handler(func=lambda call: call.data.startswith('sex'))
def an_sex_callback(query):
    data = query.data
    if data[5:] in ('Ч', 'Ж'):
        with open('lost.txt', 'a', encoding='utf-8') as lost_an_f:
            lost_an_f.write(data[5:] + '\n')
    bot.send_message(
        query.from_user.id,
        "Коли ви загубили тварину?",
        reply_markup=calendar.create_calendar(
            name=calendar_1_callback.prefix,
            year=now.year,
            month=now.month,),)


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1_callback.prefix))
def callback_inline(call: telebot.types.CallbackQuery):
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    if action == "CANCEL":
        bot.send_message(
            call.from_user.id,
            "Коли ви загубили тварину?",
            reply_markup=calendar.create_calendar(
            name=calendar_1_callback.prefix,
            year=now.year,
            month=now.month,),)
    elif action == "DAY":
        if date > now:
            bot.send_message(
            chat_id=call.from_user.id,
            text="Ви обрали дату, якої ще не було.")
            bot.send_message(
            call.from_user.id,
            "Коли ви загубили тварину?",
            reply_markup=calendar.create_calendar(
            name=calendar_1_callback.prefix,
            year=now.year,
            month=now.month,),)
        else:
            bot.send_message(
                chat_id=call.from_user.id,
                text=f"Ви обрали {date.strftime('%d.%m.%Y')}",
                reply_markup=telebot.types.ReplyKeyboardRemove())
            with open('lost.txt', 'a', encoding='utf-8') as lost_an_f:
                lost_an_f.write(date.strftime('%d.%m.%Y'))


@bot.message_handler(commands=['message'])
def handle_message(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    buttonA = telebot.types.KeyboardButton('A')
    buttonB = telebot.types.KeyboardButton('B')
    buttonC = telebot.types.KeyboardButton('C')

    markup.row(buttonA, buttonB, buttonC)

    bot.send_message(message.chat.id, 'It works!', reply_markup=markup)

bot.polling()