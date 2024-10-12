import aiofiles

async def register_log(content):
    async with aiofiles.open("logs.txt", 'a') as file:
        await file.write(content + '\n')