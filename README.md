# 🤖 Legal Documents Bot

## 🚀 Запуск бота:

1. Установите зависимости:
```bash
pip install -r requirements.txt
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
python run_bot.py

**4.2. Сохраняем служебные файлы:**
```bash
# Игнорируемые файлы для Git
cat > .gitignore << 'EOF'
venv/
.env
*.db
*.log
logs/
backups/
__pycache__/
*.pyc
