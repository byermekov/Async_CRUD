from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
import os
from dotenv import load_dotenv, find_dotenv

import handlers
from statesform import StepsForm


load_dotenv(find_dotenv())
BOT_API_TOKEN = os.environ.get("key")

bot = Bot(BOT_API_TOKEN)
dp = Dispatcher()






async def start_bot():

    dp.startup.register(handlers.on_startup)
    dp.message.register(handlers.start, Command(commands=['start']))
    dp.message.register(handlers.get_name, StepsForm.GET_NAME)
    dp.message.register(handlers.get_users, Command(commands=['people']))
    dp.message.register(handlers.restore_db, Command(commands=['restore_db']))
    dp.message.register(handlers.add_items, Command(commands=['add_items']))
    dp.message.register(handlers.get_items, StepsForm.GET_ITEMS)
    dp.message.register(handlers.insertion_finished, StepsForm.INSERTION_FINISHED)
    dp.message.register(handlers.my_items, Command(commands = ['view_items']))
    dp.message.register(handlers.get_person_items1, StepsForm.GET_PERSON1)
    dp.message.register(handlers.remove, Command(commands=['remove_items']))
    dp.message.register(handlers.get_person_items2, StepsForm.GET_PERSON2)
    dp.message.register(handlers.remove_items, StepsForm.REMOVE_ITEMS)
    dp.message.register(handlers.purchased_items, Command(commands=['purchased_items']))
    dp.message.register(handlers.get_person_items3, StepsForm.GET_PERSON3)
    dp.message.register(handlers.help_guide, Command(commands = ['help']))

    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(str(e))
    finally:
        await bot.session.close()

    

if __name__ == "__main__":
    asyncio.run(start_bot())