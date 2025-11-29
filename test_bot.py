import asyncio
import aiohttp
from core.config import Config

async def test_telegram_api():
    try:
        print("🔍 Проверяем подключение к Telegram API...")
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{Config.TOKEN}/getMe"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Подключение к Telegram API успешно!")
                    print(f"🤖 Бот: {data['result']['username']}")
                else:
                    print(f"❌ Ошибка API: {response.status}")
                    text = await response.text()
                    print(f"Ответ: {text}")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

asyncio.run(test_telegram_api())
