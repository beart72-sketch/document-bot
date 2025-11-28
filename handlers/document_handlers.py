"""Обработчики документов — исправлено под aiogram 3.x FSM"""

import logging
import os
from datetime import datetime
from io import BytesIO
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from docxtpl import DocxTemplate

logger = logging.getLogger(__name__)
document_router = Router()

# Получаем абсолютный путь к шаблону
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "contract_template.docx")

logger.info(f"📁 Путь к шаблону: {TEMPLATE_PATH}")

# Правильное объявление состояний (StatesGroup)
class DocumentStates(StatesGroup):
    collecting_name = State()
    collecting_phone = State()
    collecting_company = State()

def get_back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="create_document")
    return builder.as_markup()

@document_router.callback_query(F.data == "create_document")
async def start_document_creation(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DocumentStates.collecting_name)
    await callback.message.edit_text(
        "🔤 Введите ФИО клиента:",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@document_router.message(DocumentStates.collecting_name)
async def collect_name(message: Message, state: FSMContext):
    await state.update_data(client_name=message.text.strip())
    await state.set_state(DocumentStates.collecting_phone)
    await message.answer("📞 Введите телефон клиента:")

@document_router.message(DocumentStates.collecting_phone)
async def collect_phone(message: Message, state: FSMContext):
    await state.update_data(client_phone=message.text.strip())
    await state.set_state(DocumentStates.collecting_company)
    await message.answer("🏢 Введите название компании:")

@document_router.message(DocumentStates.collecting_company)
async def collect_company_and_generate(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    data["company_name"] = message.text.strip()
    
    # Добавляем стандартные данные
    data.update({
        "contract_number": "001",
        "city": "Москва", 
        "client_representative": data["client_name"],
        "client_basis": "Устава",
        "executor_name": "ООО 'Ваша Компания'",
        "executor_representative": "Иванов И.И.", 
        "executor_basis": "Доверенности №1",
        "contract_subject": "Оказание консультационных услуг",
        "payment_terms": "Стоимость услуг составляет 10 000 рублей.",
        "contract_term": "Настоящий Договор вступает в силу с момента подписания.",
        "client_details": data["client_name"] + ", тел: " + data["client_phone"],
        "executor_details": "ООО 'Ваша Компания', ИНН 1234567890",
        "client_signature": data["client_name"],
        "executor_signature": "Иванов И.И.",
        "date": datetime.now().strftime("%d.%m.%Y")
    })

    try:
        # Проверяем что файл существует
        if not os.path.exists(TEMPLATE_PATH):
            logger.error(f"❌ Файл не найден: {TEMPLATE_PATH}")
            await message.answer("⚠️ Шаблон документа не найден.")
            await state.clear()
            return

        logger.info(f"🔧 Генерация документа из: {TEMPLATE_PATH}")
        
        # Генерация через docxtpl
        doc = DocxTemplate(TEMPLATE_PATH)
        doc.render(data)

        # Создаем бинарный файл в памяти
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        # Создаем BufferedInputFile из байтов
        document_file = BufferedInputFile(
            file=buffer.getvalue(),
            filename="Договор.docx"
        )
        
        # Отправляем документ
        await message.answer_document(
            document=document_file,
            caption="✅ Договор сгенерирован! 📑"
        )
        
        await state.clear()
        logger.info(f"✅ Документ создан для {user_id}")

    except Exception as e:
        logger.error(f"❌ Ошибка генерации: {e}")
        await message.answer("⚠️ Ошибка при создании договора.")
        await state.clear()

async def register_document_handlers(dp):
    dp.include_router(document_router)
    logger.info("✅ Обработчики документов (docxtpl + FSM) зарегистрированы")
