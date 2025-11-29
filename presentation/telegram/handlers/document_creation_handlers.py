import logging
import datetime
import hashlib
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

logger = logging.getLogger(__name__)
document_creation_router = Router()

# Маппинг типов документов на имена шаблонов в БД
_TEMPLATE_MAP = {
    "contract": "contract_template",
    "act": "act_template", 
    "statement": "statement_template",
    "proxy": "proxy_template"
}

# Состояния для создания документа
class DocumentCreation(StatesGroup):
    waiting_for_title = State()
    waiting_for_parties = State()
    waiting_for_contract_details = State()
    waiting_for_act_details = State()
    waiting_for_statement_details = State()
    waiting_for_proxy_details = State()

# Обработчик выбора типа документа
@document_creation_router.callback_query(F.data.startswith("document_type:"))
async def document_type_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора типа документа - запускаем FSM"""
    doc_type = callback.data.split(":")[1]
    doc_types = {
        "contract": "Договор",
        "act": "Акт", 
        "statement": "Заявление",
        "proxy": "Доверенность"
    }
    
    logger.info(f"🎯 Начало создания документа '{doc_type}' от {callback.from_user.id}")
    
    # Сохраняем тип документа в состоянии
    await state.update_data(document_type=doc_type)
    
    # Запускаем процесс создания документа
    await state.set_state(DocumentCreation.waiting_for_title)
    
    text = (
        f"📝 *Создание {doc_types[doc_type]}*\n\n"
        "📌 Шаг 1 из 3\n"
        "Введите *название документа*:\n\n"
        "Пример: 'Договор оказания услуг', 'Акт приема-передачи'"
    )
    
    from presentation.telegram.keyboards import get_cancel_keyboard
    await callback.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
    await callback.answer()

# Обработчик ввода названия документа
@document_creation_router.message(DocumentCreation.waiting_for_title)
async def process_document_title(message: Message, state: FSMContext):
    """Обработчик ввода названия документа"""
    title = message.text.strip()
    
    if len(title) < 3:
        await message.answer("❌ Название слишком короткое. Введите название документа (минимум 3 символа):")
        return
    
    await state.update_data(document_title=title)
    
    # Получаем данные из состояния
    data = await state.get_data()
    doc_type = data.get('document_type')
    doc_types = {
        "contract": "Договор",
        "act": "Акт",
        "statement": "Заявление", 
        "proxy": "Доверенность"
    }
    
    # Переходим к следующему шагу в зависимости от типа документа
    if doc_type == "contract":
        await state.set_state(DocumentCreation.waiting_for_parties)
        text = (
            f"📝 *Создание {doc_types[doc_type]}*\n\n"
            "📌 Шаг 2 из 3\n"
            "Введите *стороны договора*:\n\n"
            "Формат:\n"
            "Заказчик: [ФИО/название]\n"
            "Исполнитель: [ФИО/название]\n\n"
            "Пример:\n"
            "Заказчик: ООО 'Ромашка'\n"
            "Исполнитель: Иванов Иван Иванович"
        )
    elif doc_type == "act":
        await state.set_state(DocumentCreation.waiting_for_act_details)
        text = (
            f"📝 *Создание {doc_types[doc_type]}*\n\n"
            "📌 Шаг 2 из 3\n"
            "Опишите *предмет акта*:\n\n"
            "Пример:\n"
            "Акт приема-передачи товара:\n"
            '• Товар: "Офисный стол"\n'
            "• Количество: 1 шт.\n"
            "• Состояние: новое"
        )
    elif doc_type == "statement":
        await state.set_state(DocumentCreation.waiting_for_statement_details)
        text = (
            f"📝 *Создание {doc_types[doc_type]}*\n\n"
            "📌 Шаг 2 из 3\n"
            "Введите *текст заявления*:\n\n"
            "Пример:\n"
            "Прошу предоставить мне ежегодный оплачиваемый отпуск с 01.01.2024 по 14.01.2024 продолжительностью 14 календарных дней."
        )
    elif doc_type == "proxy":
        await state.set_state(DocumentCreation.waiting_for_proxy_details)
        text = (
            f"📝 *Создание {doc_types[doc_type]}*\n\n"
            "📌 Шаг 2 из 3\n"
            "Введите *данные для доверенности*:\n\n"
            "Формат:\n"
            "Доверитель: [ФИО]\n"
            "Представитель: [ФИО]\n"
            "Полномочия: [описание]\n\n"
            "Пример:\n"
            "Доверитель: Петров Петр Петрович\n"
            "Представитель: Сидоров Сидор Сидорович\n"
            "Полномочия: представление интересов в суде"
        )
    
    from presentation.telegram.keyboards import get_cancel_keyboard
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")

# Обработчик для сторон договора
@document_creation_router.message(DocumentCreation.waiting_for_parties)
async def process_contract_parties(message: Message, state: FSMContext):
    """Обработчик ввода сторон договора"""
    parties_text = message.text.strip()
    
    # Простая валидация
    if "Заказчик:" not in parties_text or "Исполнитель:" not in parties_text:
        await message.answer("❌ Неверный формат. Используйте:\nЗаказчик: ...\nИсполнитель: ...")
        return
    
    await state.update_data(parties=parties_text)
    await state.set_state(DocumentCreation.waiting_for_contract_details)
    
    text = (
        "📝 *Создание Договора*\n\n"
        "📌 Шаг 3 из 3\n"
        "Опишите *условия договора*:\n\n"
        "Что должно быть включено:\n"
        "• Предмет договора\n"
        "• Стоимость и порядок оплаты\n"
        "• Сроки выполнения\n"
        "• Ответственность сторон\n\n"
        "Пример:\n"
        "Исполнитель обязуется разработать сайт, Заказчик оплачивает 50 000 руб. Срок - 30 дней."
    )
    
    from presentation.telegram.keyboards import get_cancel_keyboard
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")

# Обработчик для деталей договора
@document_creation_router.message(DocumentCreation.waiting_for_contract_details)
async def process_contract_details(message: Message, state: FSMContext):
    """Обработчик ввода деталей договора"""
    details = message.text.strip()
    
    if len(details) < 10:
        await message.answer("❌ Описание слишком короткое. Подробно опишите условия договора:")
        return
    
    # Получаем все данные
    data = await state.get_data()
    doc_type = data.get('document_type')
    title = data.get('document_title')
    parties = data.get('parties')
    
    # Генерируем документ
    await generate_and_send_document(message, state, doc_type, {
        'title': title,
        'parties': parties,
        'details': details
    })

# Упрощенные обработчики для других типов документов
@document_creation_router.message(DocumentCreation.waiting_for_act_details)
async def process_act_details(message: Message, state: FSMContext):
    """Обработчик для деталей акта"""
    details = message.text.strip()
    await process_simple_document(message, state, "act", details)

@document_creation_router.message(DocumentCreation.waiting_for_statement_details)
async def process_statement_details(message: Message, state: FSMContext):
    """Обработчик для текста заявления"""
    text = message.text.strip()
    await process_simple_document(message, state, "statement", text)

@document_creation_router.message(DocumentCreation.waiting_for_proxy_details)
async def process_proxy_details(message: Message, state: FSMContext):
    """Обработчик для данных доверенности"""
    details = message.text.strip()
    await process_simple_document(message, state, "proxy", details)

async def process_simple_document(message: Message, state: FSMContext, doc_type: str, details: str):
    """Обработчик для простых типов документов"""
    if len(details) < 10:
        await message.answer("❌ Слишком короткое описание. Подробно опишите детали:")
        return
    
    data = await state.get_data()
    title = data.get('document_title')
    
    await generate_and_send_document(message, state, doc_type, {
        'title': title,
        'details': details
    })

async def generate_and_send_document(message: Message, state: FSMContext, doc_type: str, data: dict):
    """Генерация и отправка документа"""
    try:
        # Показываем сообщение о генерации
        await message.answer("🔄 *Генерируем документ...*", parse_mode="Markdown")
        
        # === Аудит: ВКЛЮЧЕН (полная версия) ===
        from infrastructure.database.audit_db import audit_db
        import hashlib

        # Генерируем хеши
        data_str = str(sorted(data.items()))
        doc_hash = hashlib.sha256(data_str.encode()).hexdigest()[:16]
        
        # Получаем правильный хеш шаблона из БД
        template_name = _TEMPLATE_MAP.get(doc_type, f"{doc_type}_template")
        template_hash = audit_db.get_template_hash(template_name) or "fallback_hash"

        audit_id = audit_db.log_action(
            user_id=message.from_user.id,
            action=f"generate_{doc_type}",
            details={
                "title": data.get("title", "Без названия"),
                "type": doc_type,
                "fields": len(data)
            },
            resource_type="document",
            doc_hash=doc_hash,
            template_hash=template_hash
        )
        logger.info(f"✅ Аудит ID={audit_id} сохранён")
        
        # Создаем простой текстовый документ (временное решение)
        doc_content = create_simple_document(doc_type, data)
        
        # Отправляем документ как текстовое сообщение (временно)
        await message.answer(
            f"✅ *Документ создан!*\n\n"
            f"📄 *{data.get('title', 'Документ')}*\n\n"
            f"```\n{doc_content}\n```\n\n"
            f"⚡ В будущем здесь будет готовый файл .docx",
            parse_mode="Markdown"
        )
        
        # Завершаем состояние
        await state.clear()
        
        # Показываем главное меню
        from presentation.telegram.keyboards import get_main_keyboard
        await message.answer("Выберите следующее действие:", reply_markup=get_main_keyboard())
        
    except Exception as e:
        logger.error(f"❌ Ошибка генерации документа: {e}")
        await message.answer("❌ Произошла ошибка при создании документа")
        await state.clear()

def create_simple_document(doc_type: str, data: dict) -> str:
    """Создание простого текстового документа (временная заглушка)"""
    doc_types = {
        "contract": "ДОГОВОР",
        "act": "АКТ",
        "statement": "ЗАЯВЛЕНИЕ", 
        "proxy": "ДОВЕРЕННОСТЬ"
    }
    
    title = data.get('title', 'Без названия')
    details = data.get('details', '')
    parties = data.get('parties', '')
    
    document = f"{doc_types[doc_type]}\n{title}\n\n"
    
    if parties:
        document += f"СТОРОНЫ:\n{parties}\n\n"
    
    if details:
        document += f"ОСНОВНОЕ СОДЕРЖАНИЕ:\n{details}\n\n"
    
    document += f"Дата создания: {datetime.datetime.now().strftime('%d.%m.%Y')}\n"
    document += "⚠️ Это временная текстовая версия. В будущем будет файл .docx"
    
    return document

# Обработчик отмены создания документа
@document_creation_router.message(F.text == "❌ Отмена")
async def cancel_document_creation(message: Message, state: FSMContext):
    """Отмена создания документа"""
    await state.clear()
    from presentation.telegram.keyboards import get_main_keyboard
    await message.answer("❌ Создание документа отменено", reply_markup=get_main_keyboard())
