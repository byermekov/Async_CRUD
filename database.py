import aiosqlite
from aiogram import Bot
from aiogram.types import Message
import datetime
from log import register_log
import redis

red = redis.Redis(host="localhost", port=6379, db=0)


global DB
DB = "botdb.db"


async def initialize():

    async with aiosqlite.connect(DB) as conn:
        async with conn.cursor() as cur:

            create_items_query = """
                CREATE TABLE IF NOT EXISTS items (
                        item_id INTEGER PRIMARY KEY,
                        item_name TEXT NOT NULL,
                        date_entered TEXT NOT NULL,
                        purchased_already BOOLEAN,
                        person_id INTEGER,
                        FOREIGN KEY (person_id) REFERENCES people(person_id)
                )
            """
            create_people_query = """
                CREATE TABLE IF NOT EXISTS people (
                        person_id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        person_name TEXT,
                        UNIQUE(username, person_name) ON CONFLICT IGNORE
                )
            """


            await cur.execute(create_items_query)

            await cur.execute(create_people_query)
            
            await conn.commit()

    log = f"{datetime.datetime.now().strftime('%B %d, %Y')} ------- BOT DATABASE INITIALIZED" 
    print(log)
    await register_log(log)


async def delete_records():
    
    async with aiosqlite.connect(DB) as conn:
        async with conn.cursor() as cur:

            delete_items_query = "DELETE FROM items"
            delete_people_query = "DELETE FROM people"
            await cur.execute(delete_items_query)
            await conn.commit()
            await cur.execute(delete_people_query)
            await conn.commit()

    log = f"{datetime.datetime.now().strftime('%B %d, %Y')} ------- SQLITE::ALL RECORDS ARE DELETED"
    print(log)
    await register_log(log)
    
    red.flushall()
    log = f"{datetime.datetime.now().strftime('%B %d, %Y')} ------- REDIS::ALL ENTRIES ARE DELETED"


async def add_person(username, person_name):

    async with aiosqlite.connect(DB) as conn:
        async with conn.cursor() as cur:


            insert_person_query = "INSERT INTO people (person_name, username) VALUES (?, ?)"


            await cur.execute(insert_person_query, (person_name, username))
            
            await conn.commit()


    log = f"{datetime.datetime.now().strftime('%B %d, %Y')} ------- NEW USER ({username}, {person_name}) ADDED"
    print(log)
    await register_log(log)

async def get_people():

    async with aiosqlite.connect(DB) as conn:
        async with conn.cursor() as cur:


            get_query = "SELECT * FROM people"

            await cur.execute(get_query)

            people = await cur.fetchall()

            info = 'User list: \n'

            print(people)
            
            for record in people:
                print(record)  
                info += f'<b>ID: {record[0]}</b>, Username: @{record[1]}, Name: {record[2]}\n'
        

    return info
            

async def get_person(person_id):

    cached_data = await red.hgetall(f"person:{person_id}")

    if cached_data:

        username = cached_data[b'username'].decode()
        person_name = cached_data[b'person_name'].decode()
        red.close()
        await red.wait_closed()
        return username, person_name
    

    async with aiosqlite.connect(DB) as conn:
        async with conn.cursor() as cur:
            get_query = "SELECT username, person_name FROM people WHERE person_id = ?"
            await cur.execute(get_query,(person_id,))
            person_data = await cur.fetchone()

    if person_data:
        username = person_data[0]
        person_name = person_data[1]
        await red.hmset_dict(f"person:{person_id}", {'username': username, 'person_name': person_name})
        red.close()
        await red.wait_closed()
        return username, person_name

    return None, None

async def get_person_id(username, person_name):

    redis_key = f"person:{username}:{person_name}"

    person_id = red.get(redis_key)

    if person_id:
        log = f"{datetime.datetime.now().strftime('%B %d, %Y')} ------- CACHE HIT : {(person_id, username, person_name)}\n"
        print(log)
        await register_log(log)
        return int(person_id)
    

    async with aiosqlite.connect(DB) as conn:
        async with conn.cursor() as cur:
    
            get_query = "SELECT person_id FROM people WHERE username = ? AND person_name = ?"
            await cur.execute(get_query, (username, person_name))
            person_data = await cur.fetchone()
    

    if person_data:
        person_id = person_data[0]
        red.set(redis_key, person_id)
        expiration_time = 3600
        red.expire(redis_key, expiration_time)
        log = f"{datetime.datetime.now().strftime('%B %d, %Y')} ------- CACHE MISS : {(person_id, username, person_name)} CACHED SUCCESSFULLY -> EXPIRATION BY {expiration_time} SECONDS\n"
        print(log)
        await register_log(log)
        return person_id
    
    return None


async def add_item(item_name, username, person_name):

    async with aiosqlite.connect(DB) as conn:
        async with conn.cursor() as cur:
            
            insert_item_query = "INSERT INTO items (item_name, date_entered, purchased_already, person_id) VALUES (?,?,?,?)"
            purchased_already = False
            date_entered = datetime.datetime.now().strftime('%B %d, %Y')

            person_id = await get_person_id(username, person_name)

            insert_data = (item_name, date_entered, purchased_already, person_id)

            await cur.execute(insert_item_query, insert_data)

            await conn.commit()

            log = f"{datetime.datetime.now().strftime('%B %d, %Y')} ------- ITEM ADDED : {insert_data} SUCCESSFULLY\n"
            print(log)
            await register_log(log)


async def get_items(person_id):

    async with aiosqlite.connect(DB) as conn:
        async with conn.cursor() as cur:

            get_query = "SELECT * FROM items LEFT JOIN people ON people.person_id = items.person_id WHERE people.person_id = ? AND purchased_already = FALSE"
            await cur.execute(get_query, (person_id,))
            item_records = await cur.fetchall()
            person_name = item_records[0][-1]
            info = f"{person_name}'s wish list: \n"
            
            for record in item_records:
                info+=f'<u>Item ID: {record[0]}</u>, <b>Item name: {record[1]}</b>, Date entered: {record[2]}\n'
        

    return info

async def remove_item(item_id):
    
    async with aiosqlite.connect(DB) as conn:
        async with conn.cursor() as cur:

            update_query = 'UPDATE items SET purchased_already = TRUE WHERE item_id = ?'
            await cur.execute(update_query, (item_id,))
            await conn.commit()

            log = f'{datetime.datetime.now().strftime('%B %d, %Y')} ------- Item {item_id} was updated\n'
            print(log)
            await register_log(log)

async def get_purchased_items(person_id):

    async with aiosqlite.connect(DB) as conn:
        async with conn.cursor() as cur:

            get_query = "SELECT * FROM items LEFT JOIN people ON people.person_id = items.person_id WHERE people.person_id = ? AND purchased_already = TRUE"

            await cur.execute(get_query, (person_id,))
            item_records = await cur.fetchall()
            person_name = item_records[0][-1]
            info = f"{person_name}'s purchased items: \n"

            for record in item_records:
                info+=f'<u>Item ID: {record[0]}</u>, <b>Item name: {record[1]}</b>, Date entered: {record[2]}\n'

    return info