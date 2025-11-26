"""
Telegram Bot Implementation
"""
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from infrastructure.database.database import DatabaseManager
from application.use_cases.document_analysis import analyze_document
from config import Config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class LegalDocumentBot:
    def __init__(self):
        self.config = Config()
        self.db = DatabaseManager(self.config.DB_NAME)
        self.application = Application.builder().token(self.config.TOKEN).build()
        
        # Регистрация обработчиков
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update, context):
        """Обработчик команды /start"""
        user = update.effective_user
        await update.message.reply_text(
            f"Привет, {user.first_name}! 👋\n"
            "Я бот для анализа юридических документов.\n"
            "Отправьте мне текст документа для анализа."
        )
    
    async def help_command(self, update, context):
        """Обработчик команды /help"""
        help_text = """
📋 **Доступные команды:**
/start - Начать работу
/help - Получить справку

📄 **Как использовать:**
1. Отправьте текст юридического документа
2. Я проанализирую его и выделю ключевые моменты
3. Получите структурированный анализ

⚖️ **Возможности:**
- Анализ договоров
- Выявление рисков
- Проверка соответствия требованиям
        """
        await update.message.reply_text(help_text)
    
    async def handle_message(self, update, context):
        """Обработка текстовых сообщений"""
        text = update.message.text
        
        if len(text) < 50:
            await update.message.reply_text("📝 Пожалуйста, отправьте более объемный текст документа для анализа.")
            return
        
        # Показываем что бот работает
        await update.message.reply_text("⚖️ Анализирую документ...")
        
        # Здесь будет вызов use case для анализа документа
        try:
            analysis_result = await analyze_document(text)
            await update.message.reply_text(f"📊 **Результат анализа:**\n\n{analysis_result}")
        except Exception as e:
            logging.error(f"Error analyzing document: {e}")
            await update.message.reply_text("❌ Произошла ошибка при анализе документа. Попробуйте позже.")

def run_bot():
    """Запуск бота"""
    bot = LegalDocumentBot()
    
    print("🤖 Legal Document Bot запущен...")
    print("Нажмите Ctrl+C для остановки")
    
    try:
        bot.application.run_polling()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        logging.error(f"Bot error: {e}")

if __name__ == "__main__":
    run_bot()
