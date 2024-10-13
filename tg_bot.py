import telebot
from telebot import types
import requests
import pickle

bot = telebot.TeleBot('7583603805:AAE5fCWXBxKMgYJFHv13eQu3m7yw_CWuxSE')
events = ['Киберспорт', 'Спортивное программирование', 'Шахматы', 'Волейбол', 'Пауэрлифтинг']
times = ['10:00', '12:00', '14:00', '16:00', '18:00', '20:00']
week_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
ru_week_days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
KEY = input("Введите ключ доступа к БД: ")  # Изначально пароль : password


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/info":
        bot.send_message(message.from_user.id, "Добро пожаловать в спортивный клуб 'Code & Strength Club'!")
    elif message.text == "/support":
        bot.send_message(message.from_user.id, "Опишите Вашу проблему")
        bot.register_next_step_handler(message, support_question)
    elif message.text == "/registration":
        if check_registered(message.from_user.username):
            bot.send_message(message.from_user.id, "Вы уже зарегистрировались")
            return
        keyboard = types.InlineKeyboardMarkup()
        key_student = types.InlineKeyboardButton(text='Студент', callback_data='student')
        keyboard.add(key_student)
        key_grad = types.InlineKeyboardButton(text='Аспирант', callback_data='graduate')
        keyboard.add(key_grad)
        key_emp = types.InlineKeyboardButton(text='Сотрудник', callback_data='employee')
        keyboard.add(key_emp)
        bot.send_message(message.from_user.id, text="Выберите должность: ", reply_markup=keyboard)
    elif message.text == "/check_in":
        if not check_registered(message.from_user.username):
            bot.send_message(message.from_user.id, "Сначала зарегистрируйтесь: \n/registration")
            return
        with open("saved_schedule.pkl", 'rb') as file:
            schedule = pickle.load(file)
        sub_events = []
        keyboard = types.InlineKeyboardMarkup()
        for key in schedule.keys():
            if key.endswith('class'):
                if len(schedule[key]) > 0:
                    if schedule[key] not in sub_events:
                        sub_events.append(schedule[key])
                        keyboard.add(types.InlineKeyboardButton(text=schedule[key], callback_data=schedule[key]))
        print(sub_events)
        bot.send_message(message.from_user.id, text="Выберите занятие, на которое хотите записаться: ", reply_markup=keyboard)
    elif message.text == '/get_my_events':
        if not check_registered(message.from_user.username):
            bot.send_message(message.from_user.id, "Сначала зарегистрируйтесь: \n/registration")
            return
        result = requests.get('http://localhost/ddata/hs/events/v1/my_own', headers={'key': KEY, 'username': message.from_user.username})
        print(result.status_code)
        if result.status_code == 200:
            if len(result.text) > 0:
                bot.send_message(message.from_user.id, text=result.text)
                return
        bot.send_message(message.from_user.id, text="Не найдено информации")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data in events:
        keyboard = types.InlineKeyboardMarkup()
        with open("saved_schedule.pkl", 'rb') as file:
            schedule = pickle.load(file)
        for key in schedule:
            if key.endswith('class'):
                if schedule[key] == call.data:
                    keyboard.add(types.InlineKeyboardButton(
                        text=ru_week_days[week_days.index(key[0:3])] + ' ' + key[3:5] + ":00",
                        callback_data=(key[3:5] + ":00" + ' ' + key[0:3] + ' ' + call.data)))
                    # print((key[3:5] + ":00" + ' ' + key[0:3] + ' ' + call.data))
        bot.send_message(call.message.chat.id, text="Выберите время, на которое хотите записаться: ",
                         reply_markup=keyboard)
    elif call.data[0:5] in times:
        # print(call.data.split())
        dta = {'ИД': call.message.chat.id, 'Время': call.data[0:2], 'День': week_days.index(call.data.split()[1]) + 1, 'Занятие': ' '.join(call.data.split()[2:])}
        # print(dta)
        requests.post('http://localhost/ddata/hs/events/v1/check_in', headers={'key': KEY}, data=str(dta))
        bot.send_message(call.message.chat.id, text="Вы успешно записались на занятие")
    else:
        if call.data == "student":
            bot.send_message(call.message.chat.id, 'Введите номер студбилета')
            bot.register_next_step_handler(call.message, user_registration, 'student')
        elif call.data == "graduate":
            bot.send_message(call.message.chat.id, 'Введите номер удостоверения')
            bot.register_next_step_handler(call.message, user_registration, 'graduate')
        elif call.data == "employee":
            bot.send_message(call.message.chat.id, 'Введите табельный номер')
            bot.register_next_step_handler(call.message, user_registration, 'employee')


def support_question(message):
    bot.send_message(message.from_user.id, "Ваша проблема вскоре будет решена")


def user_registration(message, template):
    result = requests.get('http://localhost/ddata/hs/registration/v1/' + template, headers={'key': KEY, 'number': message.text})
    if result.status_code == 201:
        bot.send_message(message.from_user.id, "Номер введён неправильно")
        bot.register_next_step_handler(message, user_registration, template)
    elif result.status_code == 403:
        bot.send_message(message.from_user.id, "Ошибка подключения к БД. Свяжитесь с администратором")
    elif result.status_code == 200:
        bot.send_message(message.from_user.id, "Введите ФИО")
        bot.register_next_step_handler(message, check_name, result.text, template)


def check_name(message, name, user_type):
    if message.text.lower() == name.lower():
        bot.send_message(message.from_user.id, "Спасибо за регистрацию")
        dta = {"ИД": message.from_user.id, "ИмяПользователя": message.from_user.username, "ФИО": name, "Должность": user_type}
        requests.post('http://localhost/ddata/hs/registration/v1/registered', headers={'key': KEY},
                      data=str(dta))
    else:
        bot.send_message(message.from_user.id, "ФИО не совпадает")
        bot.register_next_step_handler(message, check_name, name)


def check_registered(user_id):
    result = requests.get('http://localhost/ddata/hs/registration/v1/check', headers={'key': KEY, 'username': user_id})
    if result.status_code == 201:
        return False
    return True


bot.polling(none_stop=True, interval=0)
