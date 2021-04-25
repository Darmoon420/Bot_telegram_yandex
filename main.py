from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from TOKEN import TOKEN
from time import asctime
from telegram import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Update
from random import randint
from telegram import Bot
import sqlite3
import wikipedia
import requests
import math

bot = Bot(TOKEN)

keyboard_start = [[
        InlineKeyboardButton("Время на сервере", callback_data='Время'),
        InlineKeyboardButton("Дата на сервере", callback_data='Дата'),
        InlineKeyboardButton("Курс валют", callback_data='Цены')]]

keyboard_game = [[
        InlineKeyboardButton("🗿", callback_data='камень'),
        InlineKeyboardButton("✂", callback_data='ножницы'),
        InlineKeyboardButton("📃", callback_data='бумагу')]]

keyboard_new_game = [[
        InlineKeyboardButton("Да", callback_data='new_game'),
        InlineKeyboardButton("Нет", callback_data='stop_game')]]

reply_markup_buttons_start = InlineKeyboardMarkup(keyboard_start)
reply_markup = InlineKeyboardMarkup(keyboard_game)
reply_markup_new_game = InlineKeyboardMarkup(keyboard_new_game)

con = sqlite3.connect("User.db", check_same_thread=False)
cur = con.cursor()
cur.execute(f"""CREATE TABLE IF NOT EXISTS data (
    id,
    text
);
""")

cur.execute(f"""CREATE TABLE IF NOT EXISTS Users (
    chat_id  UNIQUE,
    city
);
""")

con.commit()


def help(update, context):
    update.message.reply_text(
        f"\nВот список команд"
        f"\n/time - выводит время на сервере"
        f"\n/date - выводит дату на сервере"
        f"\n/wikipedia - выводит данные из википедии. Использование:  /wikipedia <запрос>"
        f"\n/weather - выводит погоду в указанном гроде. Использование: /weather <Город>"
        f"\n/set_timer - устанавливает таймер. Использование: /set <секунд>"
        f"\n/unset - удаляет текщий тамер"
        f"\n/new_task -  добавляет новую задачу в список. Использование: /new_task <задача>"
        f"\n/tasks - выводит список задач"
        f"\n/clear_tasks - удаляют все задачи из списка"
        f"\n/prices - выводит курс валют"
        f"\n/game - запуск игры камень, ножницы, бамага"
        f"\n/uravnenie - выодит результат решения квадратного уравнения. Использование: /uravnenie <a b c>"
        f"\n/gipotenusa - выводит гипотенузу. Использование: /gipotenusa <a c>", reply_markup=reply_markup_buttons_start
    )


def deskriminant(update, context):
    """
    Получает на вход 3 параметра.
    Возвращает дискриминант.
    """
    if len(context.args) == 3:
        a = int(context.args[0])
        b = int(context.args[1])
        c = int(context.args[2])
        discr = b ** 2 - 4 * a * c

        if discr > 0:
            x1 = (-b + math.sqrt(discr)) / (2 * a)
            x2 = (-b - math.sqrt(discr)) / (2 * a)
            update.message.reply_text("x1 = %.2f \nx2 = %.2f" % (x1, x2))

        elif discr == 0:
            x = -b / (2 * a)
            update.message.reply_text("x = %.2f" % x)

        else:
            update.message.reply_text("Корней нет")

    else:
        update.message.reply_text("Введите 3 числа")
        update.message.reply_text("Использование: /uravnenie <a b c>")


def gipotenusa(update, context):
    """
    Получает на вход 2 параметра.
    Возвращает дискриминант.
    """
    if len(context.args) == 2 and int(context.args[0]) > 0 and int(context.args[1]) > 0:
        a = int(context.args[0])
        b = int(context.args[1])
        gipot = (a**2 + b**2)**0.5
        update.message.reply_text("Гипотенуза = " + str(gipot))

    else:
        update.message.reply_text("Введите 2 положительных числа")
        update.message.reply_text("Использование: /gipotenusa <a c>")


def prices(update, context):
    """
    При вызове функции выполняет запрос и возвращает данные с ценами в формате json.
    """
    from_currency = "USD"
    to_currency = "RUB"

    from_currency_2 = "EUR"
    from_currency_3 = "GBP"

    api_key = "0ZPZD95M4QHYWI0X"
    base_url = r"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE"

    # main_url переменная хранит полный URL
    main_url = base_url + "&from_currency=" + from_currency +\
               "&to_currency=" + to_currency + "&apikey=" + api_key

    main_url_2 = base_url + "&from_currency=" + from_currency_2 +\
               "&to_currency=" + to_currency + "&apikey=" + api_key

    main_url_3 = base_url + "&from_currency=" + from_currency_3 + \
                 "&to_currency=" + to_currency + "&apikey=" + api_key
    req_ob = requests.get(main_url)
    req_ob_2 = requests.get(main_url_2)
    req_ob_3 = requests.get(main_url_3)

    # метод json возвращает формат json
    # результат содержит список вложенных словарей
    result = req_ob.json()
    result_2 = req_ob_2.json()
    result_3 = req_ob_3.json()

    update.message.reply_text(f"{from_currency}/{to_currency} "
                              f"{result['Realtime Currency Exchange Rate']['5. Exchange Rate']}" +
                              f"\n {from_currency_2}/{to_currency} "
                              f"{result_2['Realtime Currency Exchange Rate']['5. Exchange Rate']}" +
                              f"\n {from_currency_3}/{to_currency} "
                              f"{result_3['Realtime Currency Exchange Rate']['5. Exchange Rate']}")


def weather(update, context):
    """
    При вызове функции выполняет запрос и возвращает данные с погодой в формате json.
    """
    if context.args:
        city_name = ' '.join(context.args)
        cur.execute(f"UPDATE Users SET city = '{city_name}' WHERE chat_id = {update.message.chat_id}")
        con.commit()

    else:
        city_name = str(*(cur.execute(f"""SELECT city FROM Users WHERE chat_id = {update.message.chat_id}""").fetchone()))
    api_key = "cf8bf4912837247254a806184dc1c553"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    data = response.json()

    if data["cod"] != "404":
        tmp_data = data["main"]
        current_temperature = tmp_data["temp"]
        current_temperature_2 = tmp_data["feels_like"]
        current_pressure = tmp_data["pressure"]
        current_humidiy = tmp_data["humidity"]
        data_2 = data["weather"]
        weather_description = data_2[0]["description"]
        wind = data['wind']['speed']
        update.message.reply_text("Температура (в градусах): " +
              str(int(current_temperature) - 273) +
              "\n Ощущается как (в градусах): " +
              str(int(current_temperature_2) - 273) +
              "\n Ветер: " +
              str(wind) + ' м/с' +
              "\n Атмосферное давление (в единицах гПа): " +
              str(current_pressure) +
              "\n Влажность (в процентах): " +
              str(current_humidiy) +
              "\n Описание: " +
              str(weather_description))

    else:
        update.message.reply_text(" Город не найден")
        update.message.reply_text(" Использование: /weather <Город>")


def get_price():
    from_currency = "USD"
    to_currency = "RUB"

    from_currency_2 = "EUR"
    from_currency_3 = "GBP"

    api_key = "0ZPZD95M4QHYWI0X"
    base_url = r"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE"

    # main_url переменная хранит полный URL
    main_url = base_url + "&from_currency=" + from_currency + \
               "&to_currency=" + to_currency + "&apikey=" + api_key

    main_url_2 = base_url + "&from_currency=" + from_currency_2 + \
                 "&to_currency=" + to_currency + "&apikey=" + api_key

    main_url_3 = base_url + "&from_currency=" + from_currency_3 + \
                 "&to_currency=" + to_currency + "&apikey=" + api_key
    req_ob = requests.get(main_url)
    req_ob_2 = requests.get(main_url_2)
    req_ob_3 = requests.get(main_url_3)

    # метод json возвращает формат json
    # результат содержит список вложенных словарей
    result = req_ob.json()
    result_2 = req_ob_2.json()
    result_3 = req_ob_3.json()

    return (f"{from_currency}/{to_currency} "
                              f"{result['Realtime Currency Exchange Rate']['5. Exchange Rate']}" +
                              f"\n {from_currency_2}/{to_currency} "
                              f"{result_2['Realtime Currency Exchange Rate']['5. Exchange Rate']}" +
                              f"\n {from_currency_3}/{to_currency} "
                              f"{result_3['Realtime Currency Exchange Rate']['5. Exchange Rate']}")

def game(update, context):
    """
    При вызове функции создает клавиатуру с игрой.
    При нажатии одной из кнопок вызывается функция button
    """
    update.message.reply_text('Выберите камень, ножницы или бумагу', reply_markup=reply_markup)


def button(update: Update, _: CallbackContext):
    """
    Обрабатывет callback_data функции game
    """
    lst = ['камень', 'ножницы', 'бумагу']
    bot_choice = randint(0, 2)
    query = update.callback_query
    query.answer()

    if query.data == 'камень' or query.data == 'бумагу' or query.data == 'ножницы':

        if lst.index(query.data) == bot_choice:
            query.edit_message_text(text='Я тоже выбрал ' + lst[bot_choice] + ', ничья. Хотите сыграть еще раз?',
                                    reply_markup=reply_markup_new_game)

        elif query.data == 'камень' and lst[bot_choice] == 'ножницы':
            query.edit_message_text(text='Я выбрал ' + lst[bot_choice] + ', вы выиграли. Хотите сыграть еще раз?',
                                    reply_markup=reply_markup_new_game)

        elif query.data == 'ножницы' and lst[bot_choice] == 'бумагу':
            query.edit_message_text(text='Я выбрал ' + lst[bot_choice] + ', вы выиграли. Хотите сыграть еще раз?',
                                    reply_markup=reply_markup_new_game)

        elif query.data == 'бумагу' and lst[bot_choice] == 'камень':
            query.edit_message_text(text='Я выбрал ' + lst[bot_choice] + ', вы выиграли. Хотите сыграть еще раз?',
                                    reply_markup=reply_markup_new_game)

        elif query.data == 'камень' and lst[bot_choice] == 'бумагу':
            query.edit_message_text(text='Я выбрал ' + lst[bot_choice] + ', вы проиграли. Хотите сыграть еще раз?',
                                    reply_markup=reply_markup_new_game)

        elif query.data == 'бумагу' and lst[bot_choice] == 'ножницы':
            query.edit_message_text(text='Я выбрал ' + lst[bot_choice] + ', вы проиграли. Хотите сыграть еще раз?',
                                    reply_markup=reply_markup_new_game)

        elif query.data == 'ножницы' and lst[bot_choice] == 'камень':
            query.edit_message_text(text='Я выбрал ' + lst[bot_choice] + ', вы проиграли. Хотите сыграть еще раз?',
                                    reply_markup=reply_markup_new_game)

    if query.data == 'new_game':
        query.edit_message_text(text='Выберите камень, ножницы или бумагу', reply_markup=reply_markup)

    if query.data == 'stop_game':
        query.edit_message_text(text='Спасибо за игру')

    if query.data == 'Цены':
        bot.send_message(query.from_user.id, get_price())

    if query.data == 'Время':
        bot.send_message(query.from_user.id, get_time())

    if query.data == 'Дата':
        bot.send_message(query.from_user.id, get_date())


def wiki(update, context):
    """
    Возвращает данные из википедии
    """
    if context.args:
        update.message.reply_text(wikipedia.summary(' '.join(context.args)))

    else:
        update.message.reply_text("Вы не указали ключевое слово.")
        update.message.reply_text("Использование:  /wikipedia <запрос>")


def time(update, context):
    """
    Выводит текущее время на сервере.
    """
    update.message.reply_text(asctime().split()[3])


def get_time():
    return asctime().split()[3]


def date(update, context):
    """
    Выводит текущую дату на сервере.
    """
    tmp = asctime().split()
    update.message.reply_text(f'{tmp[0]} {tmp[1]} {tmp[2]} {tmp[4]}')


def get_date():
    tmp = asctime().split()
    return f'{tmp[0]} {tmp[1]} {tmp[2]} {tmp[4]}'


def set_timer(update, context):
    """
    Создает таймер
    """
    chat_id = update.message.chat_id

    try:
        # args[0] должен содержать значение аргумента (секунды таймера)
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text(
                'Извините, не умеем возвращаться в прошлое')
            return

        # Добавляем задачу в очередь
        # и останавливаем предыдущую (если она была)
        if 'job' in context.chat_data:
            job = context.chat_data['job']
            try:
                job.schedule_removal()
            except BaseException:
                pass

        new_job = context.job_queue.run_once(task, due, context=chat_id)
        # Запоминаем созданную задачу в данных чата.
        context.chat_data['job'] = new_job
        # Присылаем сообщение о том, что всё получилось.
        update.message.reply_text(f'Я засек {due} секунд')

    except (IndexError, ValueError):
        update.message.reply_text('Использование: /set <секунд>')


def set_city(update, context):
    """
    Добавляет город пользователя в базу данных
    """
    if str(cur.execute(f"""SELECT city FROM Users WHERE chat_id = {update.message.chat_id}""").fetchone()) == '(None,)':
        cur.execute(f"UPDATE Users SET city = '{update.message.text}' WHERE chat_id = {update.message.chat_id}")
        con.commit()
        print(update.message.text)


def task(context):
    """
    Функция оконачания таймера.
    """
    job = context.job
    context.bot.send_message(job.context, text='Время вышло!')


def unset_timer(update, context):
    """
    Останавливает таймер
    """
    # Проверяем, что задача ставилась
    if 'job' not in context.chat_data:
        update.message.reply_text('Нет активного таймера')
        return

    job = context.chat_data['job']
    # планируем удаление задачи (выполнится, когда будет возможность)
    job.schedule_removal()

    # и очищаем пользовательские данные
    del context.chat_data['job']
    update.message.reply_text('Остановил таймер!')


def start(update, context):
    """
    Функция которая вызвается при начале работы с пользователем
    """
    update.message.reply_text(
        "Я бот-справочник. Какая информация вам нужна?" +
        f"\nВот список команд"
        f"\n/time"
        f"\n/date"
        f"\n/wikipedia"
        f"\n/weather"
        f"\n/set_timer"
        f"\n/unset"
        f"\n/new_task"
        f"\n/tasks"
        f"\n/clear_tasks"
        f"\n/prices"
        f"\n/game"
        f"\n/uravnenie"
        f"\n/gipotenusa"
    )

    update.message.reply_text("Укажите ваш город")
    text_handler = MessageHandler(Filters.text, set_city)
    print(text_handler)

    cur.execute(f"INSERT INTO Users(chat_id) VALUES({update.message.chat_id})")
    con.commit()


def close_keyboard(update, context):
    """
    Функция для закртия Reply клавиатуры
    """
    update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


def new_task(update, context):
    if context.args:
        cur.execute(f"INSERT INTO data(id, text) VALUES({update.message.chat_id}, '{' '.join(context.args[0:])}')")
        con.commit()

        update.message.reply_text(f'Новая задача добавлена в список')

    else:
        update.message.reply_text(f'Использование: /new_task <задача>')


def clear_tasks(update, context):
    """
    Удаляет все задачи созданные пользователм
    """
    cur.execute(f"DELETE from data WHERE id = {update.message.chat_id}")
    con.commit()

    update.message.reply_text(f'Все задачи были удалены')


def tasks(update, context):
    """
    Выводит список задач пользователя
    """
    result = cur.execute(f"""SELECT text FROM data
                WHERE id = {update.message.chat_id}""").fetchall()

    if not result:
        update.message.reply_text(f'Нет планов')

    for i in range(len(result)):
        update.message.reply_text(f'{i + 1} {result[i][0]}')


def main():
    """
    Основаная функция работы бота
    """
    # Создаём объект updater. 
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Регистрируем обработчик в диспетчере.
    dp.add_handler(CommandHandler(["set", "set_timer"], set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True)
                   )

    dp.add_handler(CommandHandler("unset", unset_timer,
                                  pass_chat_data=True)
                   )

    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("time", time))
    dp.add_handler(CommandHandler("clear_tasks", clear_tasks))
    dp.add_handler(CommandHandler("game", game))
    dp.add_handler(CommandHandler("new_task", new_task))
    dp.add_handler(CommandHandler("tasks", tasks))
    dp.add_handler(CommandHandler("date", date))
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("wikipedia", wiki))
    dp.add_handler(CommandHandler("weather", weather))
    dp.add_handler(CommandHandler("prices", prices))
    dp.add_handler(CommandHandler("uravnenie", deskriminant))
    dp.add_handler(CommandHandler("gipotenusa", gipotenusa))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, set_city))
    updater.start_polling()

    updater.idle()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
