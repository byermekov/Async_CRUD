from aiogram import Bot, Dispatcher, types
from aiogram.types import Message 
import os
import asyncio
import sqlite3
import datetime
from dotenv import load_dotenv, find_dotenv
# from utils import *

load_dotenv(find_dotenv())
BOT_API_TOKEN = os.environ.get("key")


bot = Bot(BOT_API_TOKEN)

dp = Dispatcher(bot=bot)

@dp.message_handler(commands = ['start'])
async def start(message : Message):
    conn = sqlite3.connect('itemdb.db')
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
                item_id INTEGER PRIMARY KEY,
                item_name TEXT NOT NULL,
                date_entered TEXT NOT NULL,
                purchased_already BOOLEAN,
                entered_by TEXT,
                FOREIGN KEY (entered_by) REFERENCES people(username)
        )
""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS people (
                username TEXT PRIMARY KEY,
                person_name TEXT
        )
""")
    
    conn.commit()
    cur.close()
    conn.close()

    await message.answer(f'Hi. The database was initialized and instantiated. You may start using the app. Your username is {message.from_user.username}. Please enter your real name: ')
    # bot.register_next_step_handler(message, get_real_name)

def get_real_name(message):
    
    name = message.text.strip().lower()
    username = message.from_user.username
    conn = sqlite3.connect('itemdb.db')
    cur = conn.cursor()
    insert_query = "INSERT INTO people (person_name, username) VALUES (?, ?)"
    cur.execute(insert_query, (name, username))
    conn.commit()
    log = f"{datetime.datetime.now().strftime('%B %d, %Y')} ------- NEW USER {username} ADDED "
    print(log)
    with open('logs.txt','a') as myfile:
        myfile.write(log)
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, "Done.")

@bot.message_handler(commands=['users'])
def get_user_list(message):

    conn = sqlite3.connect('itemdb.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM people')
    users = cur.fetchall()
    
    info = 'User list: \n'
    print(users)
    for el in users:  
        info += f'Username: @{el[2]}, Name: {el[1]}\n'
    bot.send_message(message.chat.id, info)
    cur.close()
    conn.close()

@bot.message_handler(commands=['delete_records'])
def delete_records(message):
    conn = sqlite3.connect('itemdb.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM items")
    conn.commit()
    cur.execute("DELETE FROM people")
    conn.commit()

    
    log = f"{datetime.datetime.now().strftime('%B %d, %Y')} ------- ALL RECORDS ARE DELETED"
    print(log)
    with open('logs.txt','a') as myfile:
        myfile.write(log)
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, "All records are deleted.")



@bot.message_handler(commands=['add_item'])
def add_item(message):

    bot.send_message(message.chat.id, "Please list all items you want to add. When you finish, type 'end'")
    bot.register_next_step_handler(message, add_items)


@bot.message_handler(func=lambda message: True)
def add_items(message):


    if message.text.strip().lower() != 'end':
        date_entered = datetime.datetime.now().strftime('%B %d, %Y')
        item_name = message.text.strip().lower()
        username = message.from_user.username
        conn = sqlite3.connect('itemdb.db')
        cur = conn.cursor()
        
        insert_query = "INSERT INTO items (item_name, date_entered, entered_by, purchased_already) VALUES (?, ?, ?, ?)"
        
        data = (item_name, date_entered, username, 0)
        cur.execute(insert_query, data)
        conn.commit()
        log = f"{datetime.datetime.now().strftime('%B %d, %Y')} ------- ITEM ADDED : {data} SUCCESSFULLY\n"
        print(log)
        with open('logs.txt','a') as myfile:
            myfile.write(log)
        cur.close()
        conn.close()
    else:
        bot.reply_to(message, "Items added successfully")



@bot.message_handler(commands=['my_items'])
def my_items(message):

    username = message.from_user.username
    query = "SELECT * FROM items WHERE entered_by=? ORDER BY ABS(julianday('{current_date}') - julianday(date_entered))"
    conn = sqlite3.connect('itemdb.db')
    cur = conn.cursor()

    cur.execute(query, (username,))

    data = cur.fetchall()

    info = 'Here is the list of items you need to purchase:\n'
    for el in data:
        item_name = el[1]
        date = el[2]
        info += f"{item_name} : ({date})\n"
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, info)    


    
@bot.message_handler(commands=['items'])
def items(message):

    conn = sqlite3.connect('itemdb.db')
    cur = conn.cursor()
    query = 'SELECT DISTINCT username FROM people'
    cur.execute(query)


    names = cur.fetchall()
    info = 'Item records: \n'
    info += '_'*60+'\n'
    for username_record in names:    
        username = username_record[0]
        info += f'@{username}:\n'
        query = "SELECT * FROM items WHERE entered_by=? ORDER BY ABS(julianday('{current_date}') - julianday(date_entered))"
        cur.execute(query, (username,))
        item_records = cur.fetchall()
        for el in item_records:
            item_name = el[1]
            date = el[2]
            info += f"{item_name} : ({date})\n"
        info += '_'*60+'\n'
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, info)

@bot.message_handler(commands=['remove'])
def remove(message):

    my_items(message)

    bot.send_message(message.chat.id, "Please specify what items you want to remove separated by space. For example, bread hleb aboba")

    bot.register_next_step_handler(message, get_remove_list)

def get_remove_list(message):

    item_list = message.text.strip().split(' ')

    conn = sqlite3.connect('itemdb.db')
    cur = conn.cursor()

    for item in item_list:
        cur.execute("DELETE FROM items WHERE item_name = ?", (item,))
        conn.commit()
        log = f"{datetime.datetime.now().strftime('%B %d, %Y')} ------- DELETED {item} SUCCESSFULLY\n"
        print(log)
        with open('logs.txt','a') as myfile:
            myfile.write(log)
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, "Items are removed successfully")




async def main():
    coroutines = asyncio.gather()
    await coroutines



if __name__ == '__main__':

    asyncio.run(main())