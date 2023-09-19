import telebot
import sqlite3
from telebot import types
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

bot = telebot.TeleBot(os.getenv('TOKEN'))

@bot.message_handler(commands=['start'])
def start(message):
    marcup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('💵 Buy-in')
    # button2 = types.KeyboardButton('💰 Prize')
    button3 = types.KeyboardButton('📊 Statistic')
    marcup.add(button1, button3)

    base = sqlite3.connect('new.db')
    cur = base.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER, name varchar(50) PRIMARY KEY,'
                ' pass varchar(50), buy_in real, prize real)')
    base.commit()

    people_id = message.chat.id
    cur.execute('SELECT id FROM users WHERE id = {}'.format(people_id))
    data = cur.fetchone()
    if data is None:
        user_id = message.chat.id
        cur.execute('INSERT INTO users(id) VALUES(?)', (user_id,))
        base.commit()
        bot.send_message(message.chat.id, "🙂\nПривет, {0.first_name}!"
                                          "\nВыберите действие".format(message.from_user), reply_markup=marcup)
    else:
        bot.send_message(message.chat.id, "🙂\nС возвращением, {0.first_name}!"
                         .format(message.from_user), reply_markup=marcup)
    cur.close()
    base.close()


def buy_in(message):
    marcup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('💵 Buy-in')
    button2 = types.KeyboardButton('💰 Prize')
    button3 = types.KeyboardButton('📊 Statistic')
    marcup.add(button1, button2, button3)

    base = sqlite3.connect('new.db')
    cur = base.cursor()
    user_id = message.chat.id
    buy_in_value = message.text.strip()

    try:
        buy_in_value = float(buy_in_value)
    except ValueError:
        bot.send_message(message.chat.id, "❌\nЗначение 'Buy-in' должно быть числом.\nПопробуйте снова",
                         reply_markup=marcup)
        return

    if float(buy_in_value) <= 0:
        bot.send_message(message.chat.id, "❌\nЗначение 'Buy-in' должно быть больше нуля.\nПопробуйте снова",
                         reply_markup=marcup)
    else:
        cur.execute('INSERT INTO users (id, buy_in) VALUES (?,-ABS(?))', (user_id, buy_in_value))
        base.commit()
        bot.send_message(message.chat.id, "✅\nПринято\n\nПосле завершения - укажите Ваш Приз или, если потребуется,"
                                          " снова введите 'Buy-in.'\nХорошей игры!", reply_markup=marcup)
    cur.close()
    base.close()


def prize(message):
    marcup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('💵 Buy-in')
    button2 = types.KeyboardButton('💰 Prize')
    button3 = types.KeyboardButton('📊 Statistic')
    marcup.add(button1, button2, button3)

    base = sqlite3.connect('new.db')
    cur = base.cursor()
    user_id = message.chat.id
    prize_value = message.text.strip()

    try:
        prize_value = float(prize_value)
    except ValueError:
        bot.send_message(message.chat.id, "❌\nЗначение 'Prize' должно быть числом.\nПопробуйте снова",
                         reply_markup=marcup)
        return

    if float(prize_value) < 0:
        bot.send_message(message.chat.id, "❌\nЗначение 'Prize' не может быть отрицательным.\nПопробуйте снова",
                         reply_markup=marcup)
    elif float(prize_value) == 0:
        cur.execute('INSERT INTO users (id, prize) VALUES (?,?)', (user_id, prize_value))
        base.commit()
        bot.send_message(message.chat.id, "🆗\nЯ Вас понял", reply_markup=marcup)
    else:
        cur.execute('INSERT INTO users (id, prize) VALUES (?,?)', (user_id, prize_value))
        base.commit()
        bot.send_message(message.chat.id, "👍\nОтличная игра, {0.first_name}!".format(message.from_user),
                         reply_markup=marcup)
    cur.close()
    base.close()


@bot.message_handler(commands=['delete'])
def delete(message):
    base = sqlite3.connect('new.db')
    cur = base.cursor()
    user_id = message.chat.id
    cur.execute('DELETE FROM users WHERE id = ?', (user_id,))
    base.commit()
    bot.send_message(message.chat.id, "✅\nВаши данные удалены")
    cur.close()
    base.close()


@bot.message_handler(content_types=['text'])
def bot_message(message):
    marcup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('💵 Buy-in')
    button2 = types.KeyboardButton('💰 Prize')
    button3 = types.KeyboardButton('📊 Statistic')
    marcup.add(button1, button2, button3)

    base = sqlite3.connect('new.db')
    cur = base.cursor()
    if message.text == '💵 Buy-in':
        bot.send_message(message.chat.id, "✏️\nУкажите сумму взноса")
        bot.register_next_step_handler(message, buy_in)
    if message.text == '💰 Prize':
        bot.send_message(message.chat.id, "✏\nКак успехи?\nУкажите сумму выигрыша")
        bot.register_next_step_handler(message, prize)
    if message.text == '📊 Statistic':
        people_id = message.chat.id
        bt = cur.execute('SELECT SUM(buy_in) FROM users WHERE id = {}'.format(people_id)).fetchone()[0]
        pt = cur.execute('SELECT SUM(prize) FROM users WHERE id = {}'.format(people_id)).fetchone()[0]
        if bt is None or pt is None:
            bot.send_message(message.chat.id, "❗️\nДля построения Вашей статистики необходимо,"
                                              " чтобы Вы указали 'Buy-in' и 'Prize'")
        else:
            total = bt + pt
            if total > 0:
                bot.send_message(message.chat.id, "📊 Ваша статистика\n\n💵 Всего входов на сумму:   "
                                 + str(bt) + "\n💰 Всего призовых на сумму:   "
                                 + str(pt) + "\n🟢 Итого выиграл:   " + str(total)
                                 + "\n\nПоздравляю! Хороший результат", reply_markup=marcup)
            elif total == 0:
                bot.send_message(message.chat.id, "📊 Ваша статистика\n\n💵 Всего входов на сумму:   "
                                 + str(bt) + "\n💰 Всего призовых на сумму:   "
                                 + str(pt) + "\n🟡 Результат:   " + str(total)
                                 + "\n\nНеплохо! Остался при своих", reply_markup=marcup)
            else:
                bot.send_message(message.chat.id, "📊 Ваша статистика\n\n💵 Всего входов на сумму:   "
                                 + str(bt) + "\n💰 Всего призовых на сумму:   "
                                 + str(pt) + "\n🔴 В итоге:   " + str(total) + "\n\nВ покере такое бывает,"
                                 " что чаще проигрываешь, чем выигрываешь", reply_markup=marcup)
    if message.text != '💵 Buy-in' and message.text != '💰 Prize' and message.text != '📊 Statistic':
        bot.send_message(message.chat.id, "Сначала выберите действие, нажав на кнопку ниже: "
                                          "\n'💵 Buy-in' или '💰 Prize'")
    cur.close()
    base.close()


bot.polling(none_stop=True)
