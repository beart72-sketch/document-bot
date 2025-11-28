"""Точка входа — кратко, надёжно, расширяемо"""

import asyncio
import logging

# Настройка логирования (до импортов)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from infrastructure.bootstrap import initialize_app

async def main():
    app = await initialize_app()
    await app.dp.start_polling(app.bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.critical(f"❌ Фатальная ошибка: {e}", exc_info=True)
        raise
