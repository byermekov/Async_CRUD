from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

async def set_commands(bot : Bot):

    commands = [
        BotCommand(
            command = 'start',
            description = 'Start the bot'
        ),
        BotCommand(
            command = 'help',
            description = 'View all instructions'
        ),
        BotCommand(
            command = 'add_items',
            description = 'Add items to your wishlist!'
        ),
        BotCommand(
            command = 'view_items',
            description = "See each person's wishlist!"
        ),
        BotCommand(
            command = 'people',
            description = 'See all users who have wishlists'
        ),
        BotCommand(
            command = 'remove_items',
            description = 'Remove item(s) that you have already purchased'
        ),
        BotCommand(
            command = 'purchased_items',
            description = 'See the list of items that you have already purchased'
        ),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())