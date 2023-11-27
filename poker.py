from datetime import date, datetime
import telebot
from telebot import types
import sqlite3
import schedule
import time

BOSS = 149146807
STEK = 500
BANK_LESS_8_PEOPLE ={2500:{1:2000,2:500},3000:{1:2000,2:1000},3500:{1:2500,2:1000},4000:{1:3000,2:1000},
4500:{1:3000,2:1500},50000:{1:3500,2:1500},5500:{1:3500,2:2000},6000:{1:4000,2:2000},
6500:{1:4000,2:2500},7000:{1:4500,2:2500},7500:{1:5000,2:2500},8000:{1:5000,2:3000},8500:{1:5500,2:3000}}
BANK_MORE_8_PEOPLE={
    4000:{1:2500,2:1000,3:500},4500:{1:3000,2:1000,3:500},5000:{1:3000,2:1500,3:500},5500:{1:3500,2:1500,3:500},
    6000:{1:3500,2:2000,3:500},6500:{1:4000,2:2000,3:500},7000:{1:4500,2:2000,3:500},
    7500:{1:4500,2:2500,3:500},8000:{1:5000,2:2500,3:500},8500:{1:5000,2:2500,3:1000},
}
TURIK_IS_START = False
BLINDES = {1:{1:5,2:10},2:{1:10,2:25},3:{1:25,2:50},4:{1:50,2:100},5:{1:100,2:200}
,6:{1:150,2:300},7:{1:200,2:400},8:{1:300,2:600},9:{1:500,2:1000},10:{1:1000,2:2000}}

bot = telebot.TeleBot('TOKEN')

def sql_command(command):
    conn = sqlite3.connect("PartyPoker.sql")
    cur = conn.cursor()
    cur.execute(command)
    result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return result

def up_blinde(message):
    i =1
    users = sql_command("Select * from users")
    for user in users:
        chat_id = user[0]
        #info += f'id: {user[0]} nick: {user[1]}\n'
        bot.send_message(chat_id, f'Турнир начался\nПоднимаем блайнды каждые 30 минут(в тесте 10 сек 😂)')
        #bot.send_message(message.chat.id, f'{message.chat.id},   {user[0]}')
    while True:
        for user in users:
            chat_id = user[0]
            if i >1:
                if i<4:
                    t= 15
                else:
                    t =30
                bot.send_message(chat_id, f'Прошло {t} минут, поднимаем блайды')
            bot.send_message(chat_id, f'Малый блайнд: {BLINDES[i][1]}\nБольшой блайнд: {BLINDES[i][2]}')
        i+=1
        schedule.run_pending()
        if (i<4):
            time.sleep(900)
        else:
            time.sleep(1800)


def create_markup(dict_buttons):
    markup = telebot.types.InlineKeyboardMarkup()
    for btn_name,callback_data in dict_buttons.items():
        markup.add(telebot.types.InlineKeyboardButton(btn_name,callback_data=callback_data))
    return markup

@bot.message_handler(commands=['turik_start'])
def main(message):
    markup = create_markup({'Присоединиться к турниру 🎉':'add_to_game','Информация о турнире 🏆':'turik_info','Список участников 📜':'list_user','Докупиться 😭':'dokup'})
    #print(TURIK_IS_START)
    global TURIK_IS_START
    TURIK_IS_START = True
    
    bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}' ,reply_markup=markup)
    up_blinde(message)

@bot.message_handler(commands=['test_user'])
def main(message):
    markup = create_markup({'Присоединиться к турниру 🎉':'add_to_game','Информация о турнире 🏆':'turik_info','Список участников 📜':'list_user'})
    query = "insert into users (id,name)  values (1,'anton'),(2,'sergey'),(3,'dron'),(4,'grisha'),(5,'misha'),(6,'denis'),(7,'vasya') " 
    sql_command(query)
    bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}' ,reply_markup=markup)

@bot.message_handler(commands=['start', 'help'])
def main(message):
    markup = create_markup({'Присоединиться к турниру 🎉':'add_to_game','Информация о турнире 🏆':'turik_info','Список участников 📜':'list_user','Докупиться 😭':'dokup'})
    sql_command('create table if not exists users (ID INTEGER PRIMARY KEY , name varchar(70),count_purchase INTEGER DEFAULT 1)')
    bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}' ,reply_markup=markup)

@bot.callback_query_handler(func=lambda callback:callback.data=="add_to_game")
def add_user(callback):
    nickname = callback.from_user.username
    id = callback.from_user.id
    markup = create_markup({'Присоединиться к турниру 🎉':'add_to_game','Информация о турнире 🏆':'turik_info','Список участников 📜':'list_user','Докупиться 😭':'dokup'})
    try:
        sql_command("insert into users (id,name)  values ('%s','%s') " % (id,nickname))
        bot.send_message(callback.message.chat.id,f"{nickname}, вы присоединились к турниру",reply_markup=markup)
        bot.send_message(BOSS,f"{nickname}, присоединилился к турниру")
    except:
        bot.send_message(callback.message.chat.id,f"{nickname}, вы присоединились ранее",reply_markup=markup)

@bot.callback_query_handler(func=lambda callback:callback.data=="list_user")
def view_all_users(callback):
    markup = create_markup({'Присоединиться к турниру 🎉':'add_to_game','Информация о турнире 🏆':'turik_info','Список участников 📜':'list_user','Докупиться 😭':'dokup'})
    try:
        users = sql_command("Select * from users")
        info = ''
        for user in users:
            info += f'id: {user[0]} nick: {user[1]}\n'
        bot.send_message(callback.message.chat.id,info,reply_markup=markup)
    except:
        bot.send_message(callback.message.chat.id,"Список участников пуст")
            
@bot.callback_query_handler(func=lambda callback:callback.data=="turik_info")
def view_all_users(callback):
    markup = create_markup({'Присоединиться к турниру 🎉':'add_to_game','Информация о турнире 🏆':'turik_info','Список участников 📜':'list_user','Докупиться 😭':'dokup'})
    try:
        
        users = sql_command("Select count(*),sum(count_purchase) - count(*),sum(count_purchase) from users")
        count_users = users[0][0]
        dict = BANK_MORE_8_PEOPLE if count_users>=8 else BANK_LESS_8_PEOPLE
        
        bank = (users[0][2])*STEK
        
        if dict.get(bank,0)!=0 and count_users <8:
            
            top_place = f'🥇 место: {dict[bank][1]}\n🥈 место: {dict[bank][2]}'
        elif dict.get(bank,0)!=0 and count_users >=8:
            
            top_place = f'🥇 место: {dict[bank][1]}\n🥈 место: {dict[bank][2]}\n🥉 место: {dict[bank][3]}'
        else:
            
            top_place = 'Слишком много денег 🙈\nМне не разделить банк🥲'

        list_dokup = sql_command("Select * from users where count_purchase >1")
        dokup = '\n'
        for user in list_dokup:
            dokup += f'{user[1]} докупился {user[2]-1} раз(а)\n'
        
        bot.send_message(callback.message.chat.id,
        f'Количество игроков: {users[0][0]} 🧍\n\
Количество докупов: {users[0][1]} 💵\n\
Призовой фонд: {bank} 💰\n\
{top_place}\n\n\
Докупились: {dokup}',reply_markup=markup)
    except:
        bot.send_message(callback.message.chat.id,'Пока не сформирован',reply_markup=markup)

#@bot.message_handler(commands=['purchase'])
@bot.callback_query_handler(func=lambda callback:callback.data=="dokup")
def main(callback):
    #id = callback.message.from_user.id
    id = callback.message.chat.id
    print(id)
    sql_command("update users set count_purchase = count_purchase+1 where ID = (%s)" % (id))
    bot.send_message(callback.message.chat.id,f'Вы докупились 😭')
    bot.send_message(BOSS,f"{id}, докупился")
    
bot.polling(none_stop=True, interval=0)