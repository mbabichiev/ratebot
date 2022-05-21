import telebot
from telebot import types
import os.path
from datetime import datetime
import time
import sqlite3

files = 'files'
statictics = 'statictics'
file_doll = f'{files}/doll.txt'
file_euro = f'{files}/euro.txt'
today_doll_st = f'{statictics}/st_doll.txt'
today_euro_st = f'{statictics}/st_euro.txt'
yesterday_doll_st = f'{statictics}/yest_doll.txt'
yesterday_euro_st = f'{statictics}/yest_euro.txt'
max_doll = statictics + '/max_doll.txt'
min_doll = statictics + '/min_doll.txt'
max_euro = statictics + '/max_euro.txt'
min_euro = statictics + '/min_euro.txt'
db_dir = 'db/chats.db'

mychat = 0

text_to_change = 'Выберите'

bot = telebot.TeleBot("token")


def create_file_if_not_exist(name):
    if os.path.exists(name) == False:
        file = open(name, 'w')
        file.close()


def create_dir_if_not_exist(name):
    if os.path.exists(name) == False:
        os.mkdir(name)


def read_file(name):
    file = open(name, 'r')
    s = file.read()
    file.close()
    
    return s


def write_in_file(name, text):
    file = open(name, 'w')
    file.write(text)
    file.close()


with sqlite3.connect(db_dir) as db:

    cursor = db.cursor()

    query = 'CREATE TABLE IF NOT EXISTS chats(id INTEGER PRIMARY KEY, data VARCHAR(30));'

    cursor.execute(query)


def add_chat_in_db(chat_id):

    global db_dir

    try:
        db = sqlite3.connect(db_dir)
        cursor = db.cursor()

        cursor.execute("SELECT id FROM chats WHERE id = ?", [chat_id])

        s = cursor.fetchone()

        if s is None:
            cursor.execute('INSERT INTO chats(id, data) VALUES(?, ?)', [chat_id, 'ukrru'])
            bot.send_message(mychat, "Кто-то теперь тоже пользуется ботом")
        db.commit()

    except sqlite3.Error as e:
        print('Error: ', e)
    finally:
        cursor.close()
        db.close()


def update_db(chat_id, data):

    global db_dir

    try:
        db = sqlite3.connect(db_dir)
        cursor = db.cursor()
        cursor.execute("SELECT id FROM chats WHERE id = ?", [chat_id])

        s = cursor.fetchone()

        if s is None:
            print('id: ' + chat_id + ' not found. Creating...')
            cursor.execute('INSERT INTO chats(id, data) VALUES(?, ?)', [chat_id, data])
            print('Created.')
        else:
            cursor.execute('UPDATE chats SET data = ? WHERE id = ?', [data, chat_id])
        
        db.commit()
    except sqlite3.Error as e:
        print('Error: ', e)
    finally:
        cursor.close()
        db.close()


def take_data_from_db(chat_id):

    global db_dir

    try:
        db = sqlite3.connect(db_dir)
        cursor = db.cursor()
        cursor.execute("SELECT data FROM chats WHERE id = ?", [chat_id])

        s = cursor.fetchone()
        if s is None:
            print('id: ' + chat_id + ' not found. Creating...')
            cursor.execute('INSERT INTO chats(id, data) VALUES(?, ?)', [chat_id, 'ukrru'])
            print('Created.')
            db.commit()
            return 'ukrru'
        else:
            db.commit()
            return s[0]
    except sqlite3.Error as e:
        print('Error: ', e)
    finally:
        cursor.close()
        db.close()


def count_users_in_db():

    global db_dir
    result = ''
    try:

        db = sqlite3.connect(db_dir)
        cursor = db.cursor()
        cursor.execute('SELECT COUNT(*) from chats')
        result = cursor.fetchone()

    except sqlite3.Error as e:
        print('Error: ', e)
    finally:

        cursor.close()
        db.close()
        return result[0]


def keystart():
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Узнать курс")
    btn2 = types.KeyboardButton("Выбрать валюту")
    btn3 = types.KeyboardButton("Статистика")
    markup.row(btn1, btn2).add(btn3)
    
    return markup

def keyboard(message_id):

    s = take_data_from_db(message_id)
    
    ukr = '🇺🇦'
    ru = '🇷🇺'
    by = '🇧🇾'
    kz = '🇰🇿'
    mdl = '🇲🇩'
    pln = '🇵🇱'
    btk = '₿'
    
    if 'ukr' in s:
        ukr = ukr + '✅'

    if 'ru' in s:
        ru = ru + '✅'

    if 'by' in s:
        by = by + '✅'
        
    if 'kz' in s:
        kz = kz + '✅'
    
    if 'mdl' in s:
        mdl = mdl + '✅'
        
    if 'pln' in s:
        pln = pln + '✅'
    
    if 'btk' in s:
        btk = btk + '✅'
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn1 = types.InlineKeyboardButton(ukr, callback_data='ukr')
    btn2 = types.InlineKeyboardButton(ru, callback_data='ru')
    btn3 = types.InlineKeyboardButton(by, callback_data='by')
    btn4 = types.InlineKeyboardButton(kz, callback_data='kz')
    btn5 = types.InlineKeyboardButton(mdl, callback_data='mdl')
    btn6 = types.InlineKeyboardButton(pln, callback_data='pln')
    btn7 = types.InlineKeyboardButton(btk, callback_data='btk')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)

    return markup

def keyboard_support():

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("Отменить")
    markup.add(btn)

    return markup


def to_rus(mon):
    
    match mon:
        case 'Jan':
            return 'января'
        case 'Feb':
            return 'февраля'
        case 'Mar':
            return 'марта'
        case 'Apr':
            return 'апреля'
        case 'May':
            return 'мая'
        case 'Jun':
            return 'июня'
        case 'Jul':
            return 'июля'
        case 'Aug':
            return 'августа'
        case 'Sep':
            return 'января'
        case 'Oct':
            return 'октября'
        case 'Nov':
            return 'ноября'
        case 'Dec':
            return 'декабря'
        case _:
            return ''


def compare(new, old, v):
    
    new = new.replace(',', '.')
    new = new.replace('\xa0', '')
    old = old.replace(',', '.')
    old = old.replace('\xa0', '')
    value = float(new) - float(old)
    value = float('{:.2f}'.format(value))
    c = str(value)
    c = c.replace('.', ',')

    i = 0

    while c[i] != ',':
        i = i + 1

    if len(c) - i != 3:
        c = c + '0'

    if (value > 0):
        return ' (+' + c + ' ' + v + ') 🔼'
    if (value < 0):
        return ' (' + c + ' ' + v + ') 🔽'
    
    return ' (' + c + ' ' + v + ') ⏺'


def send_message(message, text, keyboard):

    if (message.chat.id < 0):
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode="Markdown")


def min_max_statistics(min_doll, max_doll, min_euro, max_euro):

    string = '_min / max\n$: ' + min_doll + ' / ' + max_doll + '\n' + \
        '€: ' + min_euro + ' / ' + max_euro + '_\n\n'
    
    return string


#######################################################################################################################################

@bot.message_handler(commands=["help"])
def send_help(message):

    send_message(message, '/rate - узнать курс доллара\n' + \
                     '/setcountry - выбрать валюту\n' + \
                     '/support - анонимно оставить отзыв, предложить что-нибудь или написать в техподдержку\n' + \
                     '/statistics - посмотреть статистику за последние сутки\n' + \
                     '\nСвязь с разработчиком - @StevenFoy', keystart())


@bot.message_handler(commands=["start"])
def send_start(message):
    
    add_chat_in_db(message.chat.id)
    send_message(message, 'Здравствуйте, ' + message.from_user.first_name + '.\n\n/rate - узнать курс\n' + \
                     '/setcountry - выбрать необходимую валюту (по умолчанию курсы *"Гривна"* и *"Рубль"*)\n\n' + \
                     '/help - другие команды', keystart())


@bot.message_handler(commands=["support"])
def send_support(message):

    send_message(message, 'Задайте свой вопрос или предложите что-нибудь для улучшения бота. Сообщение будет передано разработчику анонимно.\n\n' + \
        '/cancel - отменить сообщение.', keyboard_support())
    update_db(message.chat.id, take_data_from_db(message.chat.id) + 'support')


@bot.callback_query_handler(func=lambda call:True)
def callback(call):

    if call.message:
        bot.answer_callback_query(call.id)

        global text_to_change

        if text_to_change == 'Выберите':
            text_to_change = 'Bыбеpите'
        else:
            text_to_change = 'Выберите'

        s = take_data_from_db(call.message.chat.id)
        
        if call.data == 'ukr':
            if 'ukr' in s:
                s = s.replace('ukr', '')
            else:
                s = s + 'ukr'

        elif call.data == 'ru':
            if 'ru' in s:
                s = s.replace('ru', '')
            else:
                s = s + 'ru'

        elif call.data == 'by':
            if 'by' in s:
                s = s.replace('by', '')
            else:
                s = s + 'by'

        elif call.data == 'kz':
            if 'kz' in s:
                s = s.replace('kz', '')
            else:
                s = s + 'kz'

        elif call.data == 'mdl':
            if 'mdl' in s:
                s = s.replace('mdl', '')
            else:
                s = s + 'mdl'

        elif call.data == 'pln':
            if 'pln' in s:
                s = s.replace('pln', '')
            else:
                s = s + 'pln'
        
        elif call.data == 'btk':
            if 'btk' in s:
                s = s.replace('btk', '')
            else:
                s = s + 'btk'

        update_db(call.message.chat.id, s)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = text_to_change + ' необxодимую валюту:', reply_markup=keyboard(call.message.chat.id), parse_mode='Markdown')
 


@bot.message_handler(content_types=['text'])
def send_text(message):

    global mychat
    global text_to_change
    global file_doll
    global file_euro
    global yesterday_doll_st
    global yesterday_euro_st
    
    add_chat_in_db(message.chat.id)

    if message.text == '/rate' or message.text == 'Узнать курс' or message.text == '/rate@exchan_ratebot':
        #start_time = datetime.now()

        if os.path.exists('files/doll.txt') == False or os.path.exists('files/euro.txt') == False:
            bot.send_message(mychat, 'We have a problems. Id: 001. Files dont exist')
            bot.send_message(message.chat.id, 'Извините, возникли технические неполадки. Попробуйте позже')
        
        value_doll = read_file(file_doll)
        value_euro = read_file(file_euro)

        if value_doll == '' or value_euro == '':
            bot.send_message(mychat, 'We have a problems. Id: 002. Files is empty')
            bot.send_message(message.chat.id, 'Извините, возникли технические неполадки. Попробуйте позже')
        else:
            arr_doll = value_doll.split('\n')
            arr_euro = value_euro.split('\n')

            rate_message = ''

            s = take_data_from_db(message.chat.id)

            max_doll_from_file = read_file(max_doll)
            min_doll_from_file = read_file(min_doll)
            max_euro_from_file = read_file(max_euro)
            min_euro_from_file = read_file(min_euro)

            max_doll_from_file = max_doll_from_file.split('\n')
            min_doll_from_file = min_doll_from_file.split('\n')
            max_euro_from_file = max_euro_from_file.split('\n')
            min_euro_from_file = min_euro_from_file.split('\n')

            if 'ukr' in s:
                ukr = '*Украина (UAH)* 🇺🇦:\n\n1$ = ' + arr_doll[1] + ' ₴\n1€ = ' + arr_euro[1] + ' ₴\n\n' + min_max_statistics(min_doll_from_file[1], max_doll_from_file[1], min_euro_from_file[1], max_euro_from_file[1])

                rate_message = rate_message + ukr

            if 'ru' in s:
                ru = '*Россия (RUB)* 🇷🇺:\n\n1$ = ' + arr_doll[0] + ' ₽\n1€ = ' + arr_euro[0] + ' ₽\n\n' + min_max_statistics(min_doll_from_file[0], max_doll_from_file[0], min_euro_from_file[0], max_euro_from_file[0])
                rate_message = rate_message + ru

            if 'by' in s:
                by = '*Беларусь (BYN)* 🇧🇾:\n\n1$ = ' + arr_doll[2] + ' Br\n1€ = ' + arr_euro[2] + ' Br\n\n' + min_max_statistics(min_doll_from_file[2], max_doll_from_file[2], min_euro_from_file[2], max_euro_from_file[2])
                rate_message = rate_message + by

            if 'kz' in s:
                kz = '*Казахстан (KZT)* 🇰🇿:\n\n1$ = ' + arr_doll[3] + ' ₸\n1€ = ' + arr_euro[3] + ' ₸\n\n' + min_max_statistics(min_doll_from_file[3], max_doll_from_file[3], min_euro_from_file[3], max_euro_from_file[3])
                rate_message = rate_message + kz
            
            if 'mdl' in s:
                mdl = '*Молдавия (MDL)* 🇲🇩:\n\n1$ = ' + arr_doll[4] + ' L\n1€ = ' + arr_euro[4] + ' L\n\n' + min_max_statistics(min_doll_from_file[4], max_doll_from_file[4], min_euro_from_file[4], max_euro_from_file[4])
                rate_message = rate_message + mdl
            
            if 'pln' in s:
                pln = '*Польша (PLN)* 🇵🇱:\n\n1$ = ' + arr_doll[5] + ' zł\n1€ = ' + arr_euro[5] + ' zł\n\n' + min_max_statistics(min_doll_from_file[5], max_doll_from_file[5], min_euro_from_file[5], max_euro_from_file[5])
                rate_message = rate_message + pln
            
            if 'btk' in s:
                rate_message = rate_message + '*Bitcoin (BTK) ₿*:\n\n1₿ (BTK) = ' + arr_doll[6] + ' $ (USD)\n1₿ (BTK) = ' + arr_euro[6] + ' € (EUR)\n\n' + min_max_statistics(min_doll_from_file[6], max_doll_from_file[6], min_euro_from_file[6], max_euro_from_file[6])

            if rate_message == '':
                bot.send_message(message.chat.id, text_to_change + ' необходимую валюту:', reply_markup=keyboard(message.chat.id))
            else:

                t = time.ctime(int(arr_doll[len(arr_doll) - 1]))
                t = t.split(' ')

                add = t[3][:8]
                if len(add) != 8:
                    add = t[4][:8]

                rate_message = rate_message + '*Данные обновлены в ' + add + ' (МСК).*'
                send_message(message, rate_message, keystart())
        #print(datetime.now() - start_time)
        bot.send_message(mychat, "Кто-то узнает курс")
        
    elif message.text == '/setcountry' or message.text == 'Выбрать валюту' or  message.text == '/setcountry@exchan_ratebot':
        bot.send_message(message.chat.id, text_to_change + ' необходимую валюту:', reply_markup=keyboard(message.chat.id))
        bot.send_message(mychat, "Кто-то выбирает валюту")
    
    elif (message.text == '/statistics' or message.text == '/statistics@exchan_ratebot' or message.text == 'Статистика'):

        r_doll = read_file(yesterday_doll_st)
        r_euro = read_file(yesterday_euro_st)

        r_doll = r_doll.split('\n')
        r_euro = r_euro.split('\n')

        t = time.ctime(int(r_doll[0]))
        t = t.split(' ')

        ans = ''
        s = take_data_from_db(message.chat.id)

        value_doll = read_file(file_doll)
        value_euro = read_file(file_euro)

        arr_doll = value_doll.split('\n')
        arr_euro = value_euro.split('\n')


        if 'ukr' in s:
            ukr = '*Украина (UAH)* 🇺🇦:\n\n1$ = ' + r_doll[2] + ' ₴' + compare(arr_doll[1], r_doll[2], '₴') + '\n1€ = ' + r_euro[2] + ' ₴' + compare(arr_euro[1], r_euro[2], '₴') + '\n\n'
            ans = ans + ukr

        if 'ru' in s:
            ru = '*Россия (RUB)* 🇷🇺:\n\n1$ = ' + r_doll[1] + ' ₽' + compare(arr_doll[0], r_doll[1], '₽') + '\n1€ = ' + r_euro[1] + ' ₽' + compare(arr_euro[0], r_euro[1], '₽') + '\n\n'
            ans = ans + ru

        if 'by' in s:
            by = '*Беларусь (BYN)* 🇧🇾:\n\n1$ = ' + r_doll[3] + ' Br' + compare(arr_doll[2], r_doll[3], 'Br') + '\n1€ = ' + r_euro[3] + ' Br' + compare(arr_euro[2], r_euro[3], 'Br') + '\n\n'
            ans = ans + by

        if 'kz' in s:
            kz = '*Казахстан (KZT)* 🇰🇿:\n\n1$ = ' + r_doll[4] + ' ₸' + compare(arr_doll[3], r_doll[4], '₸') + '\n1€ = ' + r_euro[4] + ' ₸' + compare(arr_euro[3], r_euro[4], '₸') + '\n\n'
            ans = ans + kz
        
        if 'mdl' in s:
            if len(r_doll) > 6:
                mld = '*Молдавия (MDL)* 🇲🇩:\n\n1$ = ' + r_doll[5] + ' L' + compare(arr_doll[4], r_doll[5], 'L') + '\n1€ = ' + r_euro[5] + ' L' + compare(arr_euro[4], r_euro[5], 'L') + '\n\n'
                ans = ans + mld

        if 'pln' in s:
            if len(r_doll) > 7:
                pln = '*Польша (PLN)* 🇵🇱:\n\n1$ = ' + r_doll[6] + ' zł' + compare(arr_doll[5], r_doll[6], 'zł') + '\n1€ = ' + r_euro[6] + ' zł' + compare(arr_euro[5], r_euro[6], 'zł') + '\n\n'
                ans = ans + pln

        if 'btk' in s:
            ans = ans + '*Bitcoin (BTK) ₿*:\n\n1₿ (BTK) = ' + r_doll[7] + ' $' +  compare(arr_doll[6], r_doll[7], '$') + '\n1₿ (BTK) = ' + r_euro[7] + ' €' + compare(arr_euro[6], r_euro[7], '€') + '\n\n'

        if(t[3] == ''): 
            bot.send_message(message.chat.id, 'Произошла ошибка. Попробуйте позжe')
            bot.send_message(mychat, 'we have a problems. id: 003')
        else:

            if ans == '':
                bot.send_message(message.chat.id, text_to_change + ' необходимую валюту:', reply_markup=keyboard(message.chat.id))
                bot.send_message(mychat, "Кто-то выбирал статистику, но теперь выбирает валюту")
            else:

                add = t[3][:5]
                if len(add) != 5:
                    add = t[4][:5]
                    
                send_message(message, 'Курс доллара и евро ' + t[2] + ' ' + to_rus(t[1]) + ' в ' + add + ' (МСК) составил:\n\n' + ans, keystart())
                bot.send_message(mychat, 'Кто-то смотрит статистику')
        

    elif 'Answer' in message.text and message.from_user.username == 'StevenFoy':
        answ = message.text.split('\n')
        
        s = ''
        if len(answ) > 2:
            i = 2
            while i < len(answ):
                s = s + answ[i] + '\n'
                i = i + 1
            
            bot.send_message(int(answ[1]), s)
            bot.send_message(mychat, 'Сообщение отправлено: ' + s)
            

    elif 'To all' in message.text and message.from_user.username == 'StevenFoy':
        bot.send_message(mychat, 'Команда времена недоступна')
        #answ = message.text.split('\n')

        #s = ''
        #if len(answ) > 1:
        #    i = 1
        #    while i < len(answ):
        #        s = s + answ[i] + '\n'
        #        i = i + 1
            
        #    files = os.listdir(chats_dir)

        #    for c in files:
        #        try:
        #            bot.send_message(c[:-4], s)
        #            time.sleep(1)
        #        except Exception as e:
        #            bot.send_message(mychat, 'Не дошло: ' + c[:-4])

        #    bot.send_message(mychat, 'Все пользователи получили сообщение')
        
    
    elif message.text == '/count' and message.from_user.username == 'StevenFoy':

        bot.send_message(message.chat.id, 'Количество пользователей: ' + str(count_users_in_db()))
        bot.send_message(mychat, "@" + message.from_user.username + ' смотрит количество пользователей')


    s = take_data_from_db(message.chat.id)

    if 'support' in s:
        s = s.replace('support', '')

        if message.text == '/cancel' or message.text.lower() == 'отменить' or message.text == '/cancel@exchan_ratebot':
            send_message(message, 'Отменено.', keystart())
        else:
            send_message(message, 'Спасибо за сообщение. Вы также можете обратиться к создателю бота напрямую.\nСвязь - @StevenFoy', keystart())
            bot.send_message(mychat, "id: " + str(message.chat.id) + ': ' + str(message.text))

        update_db(message.chat.id, s)



