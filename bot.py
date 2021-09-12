import os
import telebot
from telebot.types import Message
import telebot_calendar
import datetime
from telebot_calendar import Calendar, CallbackData

from conf import tok
import database
import location

RADIUS = 3

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
    username = message.from_user.username
    if database.is_new_user(username):
        bot.send_message(message.chat.id, "Уведіть адресу свого будинку або надішліть його геолокацію, будь ласка.")
        bot.register_next_step_handler_by_chat_id(message.chat.id, address)


def address(message):
    coord = None
    if message.location is not None:
        coord = message.location.latitude, message.location.longitude
    if not coord:
        addr = message.text
        coord = location.find_house_coordinates(addr)
        if not coord:
            bot.send_message(message.chat.id, "Вибачте, введена адреса не знайдена.\nСпробуйте, будь ласка, ще раз.")
            bot.register_next_step_handler_by_chat_id(message.chat.id, address)
    if coord:
        database.add_user(message.from_user.username, coord[0], coord[1], message.chat.id)
        bot.send_message(message.chat.id, "Дякуємо! Ви успішно зареєструвались.")


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
        txt_file = str(query.from_user.id) + '.txt'
        with open(txt_file, 'w', encoding='utf-8') as lost_an_f:
            lost_an_f.write(data[6:] + '\n')
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton('Ч', callback_data='sex: Ч'))
        keyboard.row(telebot.types.InlineKeyboardButton('Ж', callback_data='sex: Ж'))
        bot.send_message(query.from_user.id, 'Якої статі ваша тварина?', reply_markup=keyboard)


def get_animal_type(message):
    anim_type = message.text
    txt_file = str(message.from_user.id) + '.txt'
    with open(txt_file, 'w', encoding='utf-8') as lost_an_f:
        lost_an_f.write(anim_type + '\n')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton('Ч', callback_data='sex: Ч'))
    keyboard.row(telebot.types.InlineKeyboardButton('Ж', callback_data='sex: Ж'))
    bot.send_message(message.chat.id, 'Якої статі ваша тварина?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('sex'))
def an_sex_callback(query):
    data = query.data
    if data[5:] in ('Ч', 'Ж'):
        txt_file = str(query.from_user.id) + '.txt'
        with open(txt_file, 'a', encoding='utf-8') as lost_an_f:
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

            txt_file = str(call.from_user.id) + '.txt'
            with open(txt_file, 'a', encoding='utf-8') as lost_an_f:
                lost_an_f.write(date.strftime('%d.%m.%Y') + '\n')

            with open(txt_file, 'r', encoding='utf-8') as lost_an_f:
                an_type = lost_an_f.readline().strip()
                an_sex = lost_an_f.readline().strip()
                an_date = lost_an_f.readline().strip()
            found = database.find_among_found(an_type, an_sex, an_date)

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
    txt_file = str(message.from_user.id) + '.txt'
    with open(txt_file, 'a', encoding='utf-8') as lost_an_f:
        lost_an_f.write(lost_name + '\n')
    bot.send_message(message.chat.id, "Де загубилася ваша тваринка?\n\
Можете надіслати геолокацію або написати місце текстом.")
    bot.register_next_step_handler_by_chat_id(message.chat.id, lost_address)


def lost_address(message):
    coord = None
    if message.location is not None:
        coord = message.location.latitude, message.location.longitude
    if not coord:
        addr = message.text
        coord = location.find_house_coordinates(addr)
        if not coord:
            bot.send_message(message.chat.id, "Вибачте, введена адреса не знайдена.\nСпробуйте, будь ласка, ще раз.")
            bot.register_next_step_handler_by_chat_id(message.chat.id, lost_address)
    if coord:
        txt_file = str(message.from_user.id) + '.txt'
        with open(txt_file, 'a', encoding='utf-8') as lost_an_f:
            lost_an_f.write(coord[0] + ', ' + coord[1] + '\n')
        bot.send_message(message.chat.id, "Надішліть, будь ласка, фотографію вашої тварини.")
        bot.register_next_step_handler_by_chat_id(message.chat.id, anim_photo)


def anim_photo(message):
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    img_file = str(message.from_user.id) + '.jpg'
    with open(img_file, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.chat.id, "Які особливі прикмети є у вашого улюбленця?")
    bot.register_next_step_handler_by_chat_id(message.chat.id, features)


def features(message):
    an_feat = message.text
    userId = str(message.from_user.id)
    txt_file = userId + '.txt'
    img_file = userId + '.jpg'
    with open(txt_file, 'a', encoding='utf-8') as lost_an_f:
        lost_an_f.write(an_feat + '\n')
    place, msg, photo = database.add_lost_advert(message.from_user.username, txt_file, img_file)
    os.remove(txt_file)
    os.remove(img_file)
    bot.send_message(message.chat.id, "Дякуємо за звернення. \
Слідкуйте за своїми повідомленнями в Телеграмі.")
    send_adv_in_radius(place, msg, photo)


@bot.message_handler(commands=['found'])
def handle_found(message):
    """
    Handles the found animal.
    Sends it's description to potential owners.
    """
    keyboard = telebot.types.InlineKeyboardMarkup()
    animal_types = ['Кіт', 'Собака', 'Інше']
    for anim_type in animal_types:
        keyboard.row(telebot.types.InlineKeyboardButton(anim_type, callback_data=f'found_type: {anim_type}'))
    bot.send_message(message.chat.id, 'Яку тварину ви знайшли?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('found_type'))
def found_an_type_callback(query):
    data = query.data[12:]
    if data== 'Інше':
        bot.send_message(query.from_user.id, "Уточніть, яку тварину ви знайшли, будь ласка.")
        bot.register_next_step_handler_by_chat_id(query.from_user.id, get_found_animal_type)
    elif data in ('Кіт', 'Собака'):
        txt_file = str(query.from_user.id) + '.txt'
        with open(txt_file, 'w', encoding='utf-8') as found_an_f:
            found_an_f.write(data + '\n')
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton('Ч', callback_data='found_sex: Ч'))
        keyboard.row(telebot.types.InlineKeyboardButton('Ж', callback_data='found_sex: Ж'))
        keyboard.row(telebot.types.InlineKeyboardButton('Невідомо', callback_data='found_sex: Н'))
        bot.send_message(query.from_user.id, 'Якої статі знайдена тварина?', reply_markup=keyboard)


def get_found_animal_type(message):
    anim_type = message.text
    txt_file = str(message.from_user.id) + '.txt'
    with open(txt_file, 'w', encoding='utf-8') as found_an_f:
        found_an_f.write(anim_type + '\n')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton('Ч', callback_data='found_sex: Ч'))
    keyboard.row(telebot.types.InlineKeyboardButton('Ж', callback_data='found_sex: Ж'))
    keyboard.row(telebot.types.InlineKeyboardButton('Невідомо', callback_data='found_sex: Н'))
    bot.send_message(message.chat.id, 'Якої статі знайдена тварина?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('found_sex'))
def found_an_sex_callback(query):
    data = query.data[11:]
    txt_file = str(query.from_user.id) + '.txt'
    if data in ('Ч', 'Ж', 'Н'):
        with open(txt_file, 'a', encoding='utf-8') as found_an_f:
            found_an_f.write(data + '\n')

    with open(txt_file, 'r', encoding='utf-8') as found_an_f:
        an_type = found_an_f.readline().strip()
        an_sex = found_an_f.readline().strip()
    lost = database.find_among_lost(an_type, an_sex)

    if lost:
        bot.send_message(query.from_user.id, "Перевірте, чи немає знайденої тварини \
серед останніх втрачених улюбленців. Якщо якесь оголошення містить схожу тварину, \
зв'яжіться з власником.")
        for announcement, photo in lost:
            if photo:
                bot.send_photo(query.from_user.id, photo, caption=announcement)
            else:
                bot.send_message(query.from_user.id, announcement)        
        next_m = "Ви досі маєте потребу у створенні оголошення \
чи вже знайшли власника тварини?"
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton('Досі потрібно оголошення', callback_data='found_announc: yes'))
        keyboard.row(telebot.types.InlineKeyboardButton('Дякую, тваринка знайшлася!', callback_data='found_announc: no'))
        bot.send_message(query.from_user.id, next_m, reply_markup=keyboard)
    else:
        bot.send_message(query.from_user.id, "Де ви знайшли цю тварину?")
        bot.register_next_step_handler_by_chat_id(query.from_user.id, found_anim_place)


@bot.callback_query_handler(func=lambda call: call.data.startswith('found_announc'))
def found_announc_callback(query):
    data = query.data[15:]
    if data == 'yes':
        bot.send_message(query.from_user.id, "Де ви знайшли цю тварину?")
        bot.register_next_step_handler_by_chat_id(query.from_user.id, found_anim_place)
    else:
        bot.send_message(query.from_user.id, "Дякуємо за допомогу! Ваш внесок важливий для нас❤️")


def found_anim_place(message):
    found_place = message.text
    txt_file = str(message.from_user.id) + '.txt'
    with open(txt_file, 'a', encoding='utf-8') as found_an_f:
        found_an_f.write(found_place + '\n')
    bot.send_message(message.chat.id, "Надішліть, будь ласка, фотографію знайденої тварини.")
    bot.register_next_step_handler_by_chat_id(message.chat.id, found_anim_photo)


def found_anim_photo(message):
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    img_file = str(message.from_user.id) + '.jpg'
    with open(img_file, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.chat.id, "Які особливі прикмети має знайдена тварина?")
    bot.register_next_step_handler_by_chat_id(message.chat.id, found_features)


def found_features(message):
    an_features = message.text
    userId = str(message.from_user.id)
    txt_file = userId + '.txt'
    img_file = userId + '.jpg'
    with open(txt_file, 'a', encoding='utf-8') as found_an_f:
        found_an_f.write(an_features + '\n')
    place, msg, photo = database.add_found_advert(message.from_user.username, txt_file, img_file)
    os.remove(txt_file)
    os.remove(img_file)
    bot.send_message(message.chat.id, "Дякуємо за звернення. \
Слідкуйте за своїми повідомленнями в Телеграмі.")
    send_adv_in_radius(place, msg, photo)


def send_adv_in_radius(place: str, msg: str, photo):
    contacts = database.find_users_in_radius(place, RADIUS)
    for contact in contacts:
        bot.send_photo(contact, photo, caption=msg)


@bot.message_handler(commands=['mark_found'])
def handle_mark_found(message):
    names = database.lost_animals_of_user(message.from_user.username)
    if not names:
        bot.send_message(message.chat.id, 'У вас немає загублених тварин, щоб відмічати їх знайденими.\n\
Можливо, ви хотіли викликати команду /found?')
    else:
        keyboard = telebot.types.InlineKeyboardMarkup()
        for name in names:
            keyboard.row(telebot.types.InlineKeyboardButton(name, callback_data=f'found_name: {name}'))
        keyboard.row(telebot.types.InlineKeyboardButton('Скасувати операцію', callback_data='found_name: cancel'))
        bot.send_message(message.chat.id, "Оберіть знайденого улюбленця для підтвердження операції.", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('found_name'))
def found_anim_callback(query):
    data = query.data[12:]
    if data == 'cancel':
        bot.send_message(query.from_user.id, "Операцію скасовано.")
    else:
        database.delete_lost_advert(query.from_user.username, data)
        bot.send_message(query.from_user.id, f"Вітаємо зі знаходженням {data}.")


@bot.message_handler(commands=['help'])
def handle_message(message):
    bot.send_message(message.chat.id, "Цей бот допомагає шукати загублених тварин у Львові.\n\n\
Якщо ви ніколи ним не користувалися, натисніть /start, щоб зареєструватися.\n\
Якщо ви побачили тварину, яка може бути загубленою, натисніть /found.\n\
Якщо ви загубили тварину, натисніть /lost.\nЯкщо ви знайшли свою тварину, натисніть /mark_found.\n\n\
Якщо у вас є пропозиції для покращення, звертайтеся за контактами @liubliub та @victoriya_roi.")






bot.polling()

