import telebot
import telebot_calendar
import datetime
from telebot_calendar import Calendar, CallbackData

from conf import tok
import database, location
from database import find_users_in_radius
from found_animals import get_found_animals


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
    username = message.from_user.username
    if database.is_new_user(username):
        user_id = message.chat.id
        '''
        Add user_id to db
        '''
        bot.send_message(message.chat.id, "Уведіть адресу свого будинку, будь ласка.")
        bot.register_next_step_handler_by_chat_id(message.chat.id, address)


def address(message):
    addr = message.text
    coord = location.find_house_coordinates(addr)
    if coord:
        database.add_user(message.from_user.username, coord[0], coord[1])
        bot.send_message(message.chat.id, "Дякуємо! Ви успішно зареєструвались.")
    else:
        bot.send_message(message.chat.id, "Вибачте, введена адреса не знайдена.\nСпробуйте, будь ласка, ще раз.")


@bot.message_handler(commands=['lost'])
def handle_lost(message):
    """
    Handles the lost animal.
    Helps the owner find their animal.
    """
    with open('user.txt', 'w', encoding='utf-8') as user_f:
        user_f.write(str(message.chat.id))
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
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton('Ч', callback_data='sex: Ч'))
        keyboard.row(telebot.types.InlineKeyboardButton('Ж', callback_data='sex: Ж'))
        bot.send_message(query.from_user.id, 'Якої статі ваша тварина?', reply_markup=keyboard)


def get_animal_type(message):
    anim_type = message.text
    with open('lost.txt', 'w', encoding='utf-8') as lost_an_f:
        lost_an_f.write(anim_type + '\n')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton('Ч', callback_data='sex: Ч'))
    keyboard.row(telebot.types.InlineKeyboardButton('Ж', callback_data='sex: Ж'))
    bot.send_message(message.chat.id, 'Якої статі ваша тварина?', reply_markup=keyboard)


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
                lost_an_f.write(date.strftime('%d.%m.%Y') + '\n')
            found = get_found_animals('IMG_2195.JPG')
            if found:
                bot.send_message(call.from_user.id, "Перевірте, чи немає вашого улюбленця \
серед останніх знайдених тварин. Якщо якесь оголошення може містити вашу тварину, \
зв'яжіться з людиною, яка його розмістила.")
                next_m = "Ви досі маєте потребу у створенні оголошення для пошуку тварини \
чи вже знайшли свого улюбленця?"
            for announcement, photo in found:
                if photo:
                    bot.send_photo(call.from_user.id, photo, caption=announcement)
                else:
                    bot.send_message(call.from_user.id, announcement)
            if found:
                keyboard = telebot.types.InlineKeyboardMarkup()
                keyboard.row(telebot.types.InlineKeyboardButton('Потрібно оголошення :(', callback_data='announc: yes'))
                keyboard.row(telebot.types.InlineKeyboardButton('Дякую, тваринка знайшлася!', callback_data='announc: no'))
                bot.send_message(call.from_user.id, next_m, reply_markup=keyboard)
            else:
                bot.send_message(call.from_user.id, "Як звати вашого улюбленця?")
                bot.register_next_step_handler_by_chat_id(call.from_user.id, anim_name)


@bot.callback_query_handler(func=lambda call: call.data.startswith('announc'))
def announc_callback(query):
    data = query.data[9:]
    if data == 'yes':
        bot.send_message(query.from_user.id, "Як звати вашого улюбленця?")
        bot.register_next_step_handler_by_chat_id(query.from_user.id, anim_name)
    else:
        bot.send_message(query.from_user.id, "Вітаємо з поверненням улюбленця!")


def anim_name(message):
    lost_name = message.text
    with open('lost.txt', 'a', encoding='utf-8') as lost_an_f:
        lost_an_f.write(lost_name + '\n')
    bot.send_message(message.chat.id, "Де загубилася ваша тваринка?")
    bot.register_next_step_handler_by_chat_id(message.chat.id, lost_address)


def lost_address(message):
    addr = message.text
    with open('lost.txt', 'a', encoding='utf-8') as lost_an_f:
        lost_an_f.write(addr + '\n')
    bot.send_message(message.chat.id, "Надішліть, будь ласка, фотографію вашої тварини.")
    bot.register_next_step_handler_by_chat_id(message.chat.id, anim_photo)


def anim_photo(message):
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.chat.id, "Які особливі прикмети є у вашого улюбленця?")
    bot.register_next_step_handler_by_chat_id(message.chat.id, features)


def features(message):
    an_feat = message.text
    with open('lost.txt', 'a', encoding='utf-8') as lost_an_f:
        lost_an_f.write(an_feat + '\n')
    bot.send_message(message.chat.id, "Дякуємо за звернення. \
Слідкуйте за своїми повідомленнями в Телеграмі.")
    '''
    contacts = find_users_in_radius(lat, lon, radius)
    for contact in contacts:
        bot.send_message(contact, announcement)
    '''
    # with open('user.txt', 'w', encoding='utf-8') as user_f:
    #     user_f.write(message.chat.id)
    contacts = [641607233]
    for contact in contacts:
        bot.send_message(contact, 'wooo, new message')


@bot.message_handler(commands=['message'])
def handle_message(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    buttonA = telebot.types.KeyboardButton('A')
    buttonB = telebot.types.KeyboardButton('B')
    buttonC = telebot.types.KeyboardButton('C')

    markup.row(buttonA, buttonB, buttonC)

    bot.send_message(message.chat.id, 'It works!', reply_markup=markup)

bot.polling()
