# from aiogram.types import Message
# from aiogram.fsm.context import FSMContext
# from statesform import StepsForm
# import database

# async def start(message: Message, state: FSMContext):
#     start_message = f'Hi. The database was initialized and instantiated. You may start using the app. Your username is {message.from_user.username}. Please enter your real name:'
#     await message.answer(start_message)
#     await state.set_state(StepsForm.GET_NAME)


# async def get_name(message: Message):
#     await database.add_person(message.from_user.username, message.text)
#     await message.answer("Success")


