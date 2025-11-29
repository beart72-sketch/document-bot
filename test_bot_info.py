import asyncio
import aiohttp
from core.config import Config

async def get_bot_info():
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{Config.TOKEN}/getMe"
        async with session.get(url) as response:
            data = await response.json()
            print("📋 Информация о боте:")
            print(f"ID: {data['result']['id']}")
            print(f"Имя: {data['result']['first_name']}")
            print(f"Username: @{data['result']['username']}")
            print(f"Может читать групповые сообщения: {data['result']['can_read_all_group_messages']}")
            print(f"Поддерживает инлайн: {data['result']['supports_inline_queries']}")

asyncio.run(get_bot_info())
