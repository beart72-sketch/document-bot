"""Обработчики документов — исправлено под aiogram 3.x FSM"""

import logging
from datetime import datetime
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from docxtpl import DocxTemplate

logger = logging.getLogger(__name__)
document_router = Router()

# Правильное объявление состояний (StatesGroup)
class DocumentStates(StatesGroup):
    collecting_name = State()
    collecting_phone = State()
    collecting_email = State()

def get_back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="create_document")
    return builder.as_markup()

@document_router.callback_query(F.data == "create_document")
async def start_document_creation(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DocumentStates.collecting_name)
    await callback.message.edit_text(
        "🔤 Введите ФИО для договора:",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@document_router.message(DocumentStates.collecting_name)
async def collect_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(DocumentStates.collecting_phone)
    await message.answer("📞 Введите телефон:")

@document_router.message(DocumentStates.collecting_phone)
async def collect_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await state.set_state(DocumentStates.collecting_email)
    await message.answer("📧 Введите email:")

@document_router.message(DocumentStates.collecting_email)
async def collect_email_and_generate(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    data["email"] = message.text.strip()
    data["date"] = datetime.now().strftime("%d.%m.%Y")
    
    try:
        # Генерация через docxtpl
        doc = DocxTemplate("templates/contract_template.docx")
        doc.render(data)
        
        from io import BytesIO
        buffer = BytesIO()
        doc.save(buffer)
        document_bytes = buffer.getvalue()
        
        # Отправка
        await message.answer_document(
            document=("Договор.docx", document_bytes),
            caption="✅ Договор сгенерирован! 📑"
        )
        await state.clear()
        
        logger.info(f"✅ Документ создан для {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка генерации: {e}")
        await message.answer("⚠️ Ошибка при создании договора.")

async def register_document_handlers(dp):
    dp.include_router(document_router)
    logger.info("✅ Обработчики документов (docxtpl + FSM) зарегистрированы")
