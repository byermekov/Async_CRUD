from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from statesform import StepsForm
import database
from aiogram import Bot
from commands import set_commands

wellcome_sticker_id = 'CAACAgIAAxkBAAIDBmX3FXDiseS_iUsm9fTpIcOwYKXGAALXGAACbibhSwVjLcKY6_yrNAQ'
byebye_sticker_id = 'CAACAgIAAxkBAAIDM2X3Gm1V2gTvxzO4cdHJG-mek5kqAAKaFQACGMI5ShC2EuSYReV1NAQ'


async def collect_user_data(message: Message, bot: Bot, state: FSMContext):
    global chat_id
    chat_id = message.chat.id
    message.answer(chat_id)

async def on_startup(bot: Bot):
    await database.initialize()
    await set_commands(bot)

async def help_guide(message: Message, bot: Bot):

    message_prompt = "Hi! This is a WishList Bot! I can keep track of your wishes - items that you are intending to purchase. Here is what I can do: \
                      \n/add_items: Add items to your wishlist! \
                      \n/view_items: See each person's wishlist! \
                      \n/remove_items: Remove item(s) that you have already purchased \
                      \n/purchased_items: See the list of items that you have already purchased"

    await message.answer(message_prompt)

async def start(message: Message, state: FSMContext):

    await message.answer_sticker(wellcome_sticker_id)
    start_message = f'Hi. The database was initialized and instantiated. You may start using the app. Your username is {message.from_user.username}. Please user "/help" for getting instructions.'
    await message.answer(start_message)



async def get_users(message: Message, bot: Bot):
    
    query_result = await database.get_people()

    await message.answer(query_result, parse_mode='HTML')

    

async def restore_db(message: Message, bot: Bot):
    
    await database.delete_records()
    message_deletion = "All records are deleted."
    await message.answer(message_deletion)
    await database.initialize()


async def add_items(message: Message, state : FSMContext):
    message_prompt = "Please enter your name"
    await message.answer(message_prompt)
    await state.set_state(StepsForm.GET_NAME)

async def get_name(message: Message, state: FSMContext):
    await database.add_person(message.from_user.username.lower(), message.text.lower())
    message_prompt = f'Okay, {message.from_user.username}, please list all items you want to add for {message.text}. When you finish, enter "end" TWICE!'
    await state.update_data(person_name = message.text.lower())
    await message.answer(message_prompt)
    await state.set_state(StepsForm.GET_ITEMS)

async def get_items(message: Message, state: FSMContext):

    if message.text.lower() == 'end':
        await state.set_state(StepsForm.INSERTION_FINISHED)
    else:
        state_data = await state.get_data()
        person_name = state_data.get('person_name')
        await database.add_item(message.text.lower(), message.from_user.username.lower(), person_name)
    
async def insertion_finished(message: Message, state: FSMContext):

    message_prompt = "Okay, done. Now you can see your wish list with /view_items command"

    await message.answer(message_prompt)

    await state.clear()

async def my_items(message: Message, state : FSMContext):

    query_result = await database.get_people()
    message_prompt = 'Please select the person BY ID:\n'
    message_prompt += query_result
    await message.answer(message_prompt, parse_mode='HTML')

    await state.set_state(StepsForm.GET_PERSON1)

async def get_person_items1(message: Message, state: FSMContext):
    
    person_id = int(message.text)

    items_list = await database.get_items(person_id)

    await state.clear()

    await message.answer(items_list, parse_mode='HTML')

    
async def remove(message: Message, state: FSMContext):
    
    query_result = await database.get_people()
    message_prompt = 'Please select the person BY ID:\n'
    message_prompt += query_result
    await message.answer(message_prompt, parse_mode='HTML')

    await state.set_state(StepsForm.GET_PERSON2)

async def get_person_items2(message: Message, state: FSMContext):

    person_id = int(message.text)

    message_prompt = 'Please list all the items you want to remove BY ID\n'
    items_list = await database.get_items(person_id)

    message_prompt+=items_list

    await message.answer(message_prompt, parse_mode='HTML')

    await state.set_state(StepsForm.REMOVE_ITEMS)

async def remove_items(message : Message, state : FSMContext):

    item_ids = message.text.split(' ')

    for item_id in item_ids:
        await database.remove_item(item_id)
    
    await state.clear()

    await message.answer("Success. You can see all of your purchased items using /purchased_items command.")

async def purchased_items(message: Message, state: FSMContext):
    
    query_result = await database.get_people()
    message_prompt = 'Please select the person BY ID:\n'
    message_prompt += query_result
    await message.answer(message_prompt, parse_mode='HTML')

    await state.set_state(StepsForm.GET_PERSON3)

async def get_person_items3(message : Message, state : FSMContext):
    
    person_id = int(message.text)

    items_list = await database.get_purchased_items(person_id)

    await state.clear()

    await message.answer(items_list, parse_mode='HTML')


    

