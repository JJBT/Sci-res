import telebot
from Constants import Token, Proxy
from datetime import datetime, timedelta
import content
from nltk import WordNetLemmatizer


bot = telebot.TeleBot(Token)
telebot.apihelper.proxy = {'https': Proxy}
wnl = WordNetLemmatizer()


def log(message, answer):
    print("\n ---------")
    print(datetime.now())
    print("{0} {1}\n{2}".format(message.from_user.first_name,
                                message.from_user.last_name,
                                message.text))
    print(answer)


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    user_markup.row('1 DAY', '2 DAYS', '3 DAYS')
    bot.send_message(message.from_user.id, "Description", reply_markup=user_markup)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == '1 DAY':
        answer = content.get_words(datetime.now() - timedelta(days=1))
        bot.send_message(message.from_user.id, answer)
        log(message, answer)
    elif message.text == '2 DAYS':
        answer = content.get_words(datetime.now() - timedelta(days=2))
        bot.send_message(message.from_user.id, answer)
        log(message, answer)
    elif message.text == '3 DAYS':
        answer = content.get_words(datetime.now() - timedelta(days=3))
        bot.send_message(message.from_user.id, answer)
        log(message, answer)
    else:
        answer = content.get_article(datetime.now() - timedelta(days=1), wnl.lemmatize(message.text.lower()))
        bot.send_message(message.from_user.id, answer)
        log(message, answer)


bot.polling(none_stop=True, interval=0)
