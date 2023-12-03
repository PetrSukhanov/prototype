from telebot import TeleBot, types
import mysql.connector
import telebot


bot = telebot.TeleBot('token')

mydb = mysql.connector.connect(
    host="host",
    user="user_name",
    password="pass",
    database="db_name",
)

cursor = mydb.cursor()


@bot.message_handler(commands=['start'])
def start(message):
    surname = f" {message.from_user.last_name}" if message.from_user.last_name else ''
    bot.send_message(message.chat.id,
                     f"Доброго времени суток, {message.from_user.first_name}{surname}. Введите пожалуйста ИНН вашей компании.")


@bot.message_handler(func=lambda message: True)
def get_next(message):
    conn = mydb.cursor()
    user_inn = message.text

    if user_inn == "/help":
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton("Нет документов для оплаты", callback_data='fetch_doc')
        btn2 = types.InlineKeyboardButton("Нужен акт сверки", callback_data='fetch_act')
        btn3 = types.InlineKeyboardButton("Иной вопрос", callback_data='another_question')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id,'выберите один из следующих вопросов, который мешает вам урегулировать задолженность по договорам',reply_markup=markup)

        @bot.callback_query_handler(func=lambda call: True)
        def handle_query(call):
            if call.data == 'fetch_act':
                bot.send_message(call.message.chat.id, "Введите id для обновления:")
                bot.register_next_step_handler(call.message, update_value)

        def update_value(message):
            id_value = message.text
            bot.send_message(message.chat.id, "Введите новое значение:")
            bot.register_next_step_handler(message, update_database, id_value)

        def update_database(message, id_value):
            new_value = message.text
            cursor = mydb.cursor()
            sql = "UPDATE able SET АктСверки = %s WHERE id = %s"
            val = (new_value, id_value)
            cursor.execute(sql, val)
            mydb.commit()
            cursor.close()

            bot.send_message(message.chat.id, "Значение обновлено успешно")
        return
    else:
        conn.execute("SELECT УФПС FROM able WHERE ИННдолжника = %s", (user_inn,))
        result = conn.fetchone()
        if result:
            bot.send_message(message.chat.id, "Ваш УФПС: " + str(result[0]))
        else:
            bot.send_message(message.chat.id,"Информация об организации, которую вы представляете отсутствует в базе данных должников АО Почта россии. Проверьте правильность ввода и нажмите /start, чтобы попробовать еще раз")

        conn.execute("SELECT ОДЗ FROM able WHERE ИННдолжника = %s", (user_inn,))
        result = conn.fetchone()
        if result:
            bot.send_message(message.chat.id, "Ваше ОДЗ: " + str(result[0]))

        conn.execute("SELECT ПДЗ FROM able WHERE ИННдолжника = %s", (user_inn,))
        result = conn.fetchone()
        if result:
            bot.send_message(message.chat.id, "Ваше ПДЗ: " + str(result[0]))

        conn.execute("SELECT НомерДоговора FROM able WHERE ИННдолжника = %s", (user_inn,))
        result = conn.fetchone()
        if result:
            bot.send_message(message.chat.id, "Ваш Номер Договора: " + str(result[0]))

        conn.execute("SELECT ДниПросрочкиПА FROM able WHERE ИННдолжника = %s", (user_inn,))
        result = conn.fetchone()
        if result:
            bot.send_message(message.chat.id, "У вас: " + str(result[0]) + " дней просрочки")

        conn.execute("SELECT Должник FROM able WHERE ИННдолжника = %s", (user_inn,))
        result = conn.fetchone()
        if result:
            bot.send_message(message.chat.id, "Ваша компания: " + str(result[0]))
        # conn.close()

    bot.send_message(message.chat.id, 'введите /help, чтобы получить нужные вам документы или задать вопрос поддержке')





bot.polling(none_stop=True)
