import telebot
from telebot import types
import pickle
from string import Template
import requests

bot = telebot.TeleBot('7542282643:AAGNrW03iCMenzICsL2H0HmYQXk9wkFAm4M')
week_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
guys = ['stu', 'emp', 'gra']
add_event = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
events = ['all', 'cyb', 'progr', 'chess', 'wal', 'power', '']
full_named_events = ['+', 'Киберспорт', 'Спортивное программирование', 'Шахматы', 'Волейбол', 'Пауэрлифтинг', '']




@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if not check_for_admin(message.from_user.username):
        bot.send_message(message.from_user.id, text="Для пользования ботом нужно стать администратором")
        return
    # with open("saved_schedule.pkl", 'rb') as file:
    #     schedule = pickle.load(file)
    if message.text == '/cancel_event':
        keyboard = types.InlineKeyboardMarkup()
        key_mon = types.InlineKeyboardButton(text='Понедельник', callback_data='mon')
        keyboard.add(key_mon)
        key_tue = types.InlineKeyboardButton(text='Вторник', callback_data='tue')
        keyboard.add(key_tue)
        key_wed = types.InlineKeyboardButton(text='Среда', callback_data='wed')
        keyboard.add(key_wed)
        key_thu = types.InlineKeyboardButton(text='Четверг', callback_data='thu')
        keyboard.add(key_thu)
        key_fri = types.InlineKeyboardButton(text='Пятница', callback_data='fri')
        keyboard.add(key_fri)
        key_sat = types.InlineKeyboardButton(text='Суббота', callback_data='sat')
        keyboard.add(key_sat)
        key_sun = types.InlineKeyboardButton(text='Воскресенье', callback_data='sun')
        keyboard.add(key_sun)
        bot.send_message(message.from_user.id, text="Выберите день недели, за который хотите отменить занятие: ",
                         reply_markup=keyboard)
    if message.text == '/add_event':
        keyboard = types.InlineKeyboardMarkup()
        key_mon = types.InlineKeyboardButton(text='Понедельник', callback_data='monday')
        keyboard.add(key_mon)
        key_tue = types.InlineKeyboardButton(text='Вторник', callback_data='tuesday')
        keyboard.add(key_tue)
        key_wed = types.InlineKeyboardButton(text='Среда', callback_data='wednesday')
        keyboard.add(key_wed)
        key_thu = types.InlineKeyboardButton(text='Четверг', callback_data='thursday')
        keyboard.add(key_thu)
        key_fri = types.InlineKeyboardButton(text='Пятница', callback_data='friday')
        keyboard.add(key_fri)
        key_sat = types.InlineKeyboardButton(text='Суббота', callback_data='saturday')
        keyboard.add(key_sat)
        key_sun = types.InlineKeyboardButton(text='Воскресенье', callback_data='sunday')
        keyboard.add(key_sun)
        bot.send_message(message.from_user.id, text="Выберите день недели, на который хотите добавить занятие: ",
                         reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    with open("saved_schedule.pkl", 'rb') as file:
        schedule = pickle.load(file)
    if call.data in week_days:
        keyboard = types.InlineKeyboardMarkup()
        i = 0
        for key in schedule.keys():
            if key.startswith(call.data) and key.endswith('time'):
                keyboard.add(types.InlineKeyboardButton(text=schedule[key], callback_data=key))
                i += 1
        if i == 0:
            bot.send_message(call.message.chat.id, text="На этот день не запланировано занятий")
        else:
            bot.send_message(call.message.chat.id, text="Выберите время: ",
                             reply_markup=keyboard)
    elif call.data in guys:
        pass
    elif call.data in add_event:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='10:00', callback_data=call.data[0:3] + '10class'))
        keyboard.add(types.InlineKeyboardButton(text='12:00', callback_data=call.data[0:3] + '12class'))
        keyboard.add(types.InlineKeyboardButton(text='14:00', callback_data=call.data[0:3] + '14class'))
        keyboard.add(types.InlineKeyboardButton(text='16:00', callback_data=call.data[0:3] + '16class'))
        keyboard.add(types.InlineKeyboardButton(text='18:00', callback_data=call.data[0:3] + '18class'))
        keyboard.add(types.InlineKeyboardButton(text='20:00', callback_data=call.data[0:3] + '20class'))
        bot.send_message(call.message.chat.id, text="Выберите время: ",
                          reply_markup=keyboard)
    elif call.data.endswith('time'):
        try:
            # print(call.data)
            schedule[call.data] = ''
            schedule[call.data.replace('time', 'class')] = ''
            reload(schedule)
            bot.send_message(call.message.chat.id, text="Занятие отменено")
        except KeyError:
            pass
    elif call.data.endswith('class'):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Киберспорт', callback_data='' + call.data + ' ' + '1'))
        keyboard.add(types.InlineKeyboardButton(text='Спортивное программирование', callback_data='' + call.data + ' ' + '2'))
        keyboard.add(types.InlineKeyboardButton(text='Шахматы', callback_data='' + call.data + ' ' + '3'))
        keyboard.add(types.InlineKeyboardButton(text='Волейбол', callback_data='' + call.data + ' ' + '4'))
        keyboard.add(types.InlineKeyboardButton(text='Пауэрлифтинг', callback_data='' + call.data + ' ' + '5'))
        bot.send_message(call.message.chat.id, text="Выберите занятие: ", reply_markup=keyboard)
    else:
        try:
            _ = call.data.split()[1]
            all_fields = call.data.split()
            schedule[all_fields[0]] = full_named_events[int(all_fields[1])]
            schedule[all_fields[0].replace('class', 'time')] = f'{all_fields[0][3:5]}:00 — {int(all_fields[0][3:5]) + 2}:00'
            reload(schedule)
            bot.send_message(call.message.chat.id, text="Занятие добавлено")
        except:
            pass


def reload(schedule):
    for day in week_days:
        for hours in range(10, 21, 2):
            schedule[f'{day}{hours}'] = events[full_named_events.index(schedule[f'{day}{hours}class'])]
    with open("saved_schedule.pkl", 'wb') as file:
        pickle.dump(schedule, file)
    with open('schedule_template.txt', 'r', encoding='utf-8') as file:
        src = Template(file.read())
        result = src.substitute(schedule)
        with open("schedule.html", 'w', encoding='utf-8') as htmlfile:
            htmlfile.write(result)


def check_for_admin(username):
    result = requests.get('http://localhost/ddata/hs/registration/v1/admin_check', headers={'username': username})
    if result.status_code != 200:
        print(username)
        print(result.status_code)
        return False
    return True


bot.polling(none_stop=True, interval=0)
