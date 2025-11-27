from typing import Dict, Any
from telebot.async_telebot import AsyncTeleBot
from domain.services.menu_service import MenuService
from presentation.telegram.keyboards.main_keyboards import MainKeyboards
from application.services.user_service import UserService
from application.services.document_service import DocumentService
from domain.entities.document import DocumentType
from domain.entities.menu import MenuType  # Добавляем импорт

class BotFacade:
    """Фасад для работы с ботом"""
    
    def __init__(self, bot: AsyncTeleBot, user_service: UserService, 
                 document_service: DocumentService,
                 menu_service: MenuService, keyboards: MainKeyboards):
        self.bot = bot
        self.user_service = user_service
        self.document_service = document_service
        self.menu_service = menu_service
        self.keyboards = keyboards
        self._user_document_states: Dict[int, Dict[str, Any]] = {}
    
    async def handle_start(self, message: Any) -> None:
        """Обработка команды /start"""
        user_id = message.from_user.id
        self.menu_service.set_user_state(user_id, MenuType.MAIN)
        
        # Создаем/получаем пользователя
        user = await self.user_service.get_or_create_user(
            telegram_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        print(f"👤 Пользователь: {user.first_name} (ID: {user.telegram_id})")
        
        menu = self.keyboards.create_reply_keyboard(MenuType.MAIN)
        
        await self.bot.send_message(
            message.chat.id,
            f"👋 Добро пожаловать, {user.first_name or 'пользователь'}!\n\n"
            "Я помогу вам создавать юридические документы. "
            "Выберите действие из меню ниже:",
            reply_markup=menu
        )
    
    async def handle_message(self, message: Any) -> None:
        """Обработка всех сообщений"""
        user_id = message.from_user.id
        text = message.text
        
        # Обновляем активность пользователя
        await self.user_service.update_user_activity(user_id)
        
        # Ищем обработчик для текста в меню
        handler_name = self.menu_service.get_handler_for_text(text)
        
        if handler_name:
            await getattr(self, handler_name)(message)
        else:
            user_state = self.menu_service.get_user_state(user_id)
            await self._handle_text_input(message, user_state)
    
    async def handle_create_document(self, message: Any) -> None:
        """Обработчик создания документа"""
        user_id = message.from_user.id
        self.menu_service.set_user_state(user_id, MenuType.DOCUMENT_TYPES)
        
        menu = self.keyboards.create_reply_keyboard(MenuType.DOCUMENT_TYPES)
        
        await self.bot.send_message(
            message.chat.id,
            "📋 **Выберите тип документа:**\n\n"
            "• 📃 Исковое заявление\n"
            "• 📄 Договор\n"
            "• 📑 Жалоба\n" 
            "• 📊 Ходатайство",
            reply_markup=menu
        )
    
    async def handle_document_type(self, message: Any) -> None:
        """Обработчик выбора типа документа"""
        user_id = message.from_user.id
        text = message.text
        
        # Определяем тип документа по тексту кнопки
        doc_type_map = {
            '📃 Исковое заявление': DocumentType.CLAIM,
            '📄 Договор': DocumentType.CONTRACT,
            '📑 Жалоба': DocumentType.COMPLAINT,
            '📊 Ходатайство': DocumentType.MOTION
        }
        
        doc_type = doc_type_map.get(text)
        if doc_type:
            # Сохраняем состояние создания документа
            self._user_document_states[user_id] = {
                'document_type': doc_type,
                'step': 'awaiting_title'
            }
            
            await self.bot.send_message(
                message.chat.id,
                f"📝 **Создание {text}**\n\n"
                "Введите название для вашего документа:",
                reply_markup=self.keyboards.create_reply_keyboard(MenuType.DOCUMENT_TYPES)
            )
        else:
            await self.bot.send_message(
                message.chat.id,
                "❌ Неизвестный тип документа",
                reply_markup=self.keyboards.create_reply_keyboard(MenuType.MAIN)
            )
    
    async def handle_my_documents(self, message: Any) -> None:
        """Обработчик моих документов"""
        user_id = message.from_user.id
        
        try:
            # Получаем документы пользователя
            documents_response = await self.document_service.get_user_documents(user_id)
            
            if documents_response.documents:
                response_text = "📂 **Ваши документы:**\n\n"
                for i, doc in enumerate(documents_response.documents, 1):
                    status_emoji = {
                        'draft': '📄',
                        'in_progress': '🔄', 
                        'completed': '✅',
                        'archived': '📦'
                    }.get(doc.status, '📄')
                    
                    response_text += (
                        f"{i}. {status_emoji} **{doc.title}**\n"
                        f"   Тип: {self._get_document_type_name(doc.document_type)}\n"
                        f"   Статус: {self._get_status_name(doc.status)}\n"
                        f"   Создан: {doc.created_at.strftime('%d.%m.%Y')}\n\n"
                    )
                
                response_text += f"📊 Всего документов: {documents_response.total_count}/{documents_response.user_document_limit}"
                
            else:
                response_text = (
                    "📂 **Ваши документы**\n\n"
                    "У вас пока нет созданных документов.\n"
                    "Нажмите '📋 Создать документ' чтобы начать!"
                )
            
            await self.bot.send_message(message.chat.id, response_text)
            
        except Exception as e:
            print(f"❌ Ошибка при получении документов: {e}")
            await self.bot.send_message(
                message.chat.id,
                "❌ Произошла ошибка при загрузке документов. Попробуйте позже."
            )
    
    async def handle_settings(self, message: Any) -> None:
        """Обработчик настроек"""
        await self.bot.send_message(
            message.chat.id,
            "⚙️ **Настройки**\n\n"
            "Раздел находится в разработке."
        )
    
    async def handle_help(self, message: Any) -> None:
        """Обработчик помощи из меню"""
        await self.bot.send_message(
            message.chat.id,
            "📖 **Помощь по боту**\n\n"
            "• 📋 Создать документ - создание новых юридических документов\n"
            "• 📁 Мои документы - просмотр созданных документов\n"
            "• ⚙️ Настройки - настройки аккаунта\n"
            "• ℹ️ Помощь - это сообщение\n\n"
            "Для начала работы используйте меню ниже."
        )
    
    async def handle_back(self, message: Any) -> None:
        """Обработчик кнопки Назад"""
        user_id = message.from_user.id
        
        # Очищаем состояние создания документа
        if user_id in self._user_document_states:
            del self._user_document_states[user_id]
        
        self.menu_service.set_user_state(user_id, MenuType.MAIN)
        
        menu = self.keyboards.create_reply_keyboard(MenuType.MAIN)
        
        await self.bot.send_message(
            message.chat.id,
            "🔙 Возвращаемся в главное меню:",
            reply_markup=menu
        )
    
    async def _handle_text_input(self, message: Any, user_state) -> None:
        """Обработка произвольного текстового ввода"""
        user_id = message.from_user.id
        text = message.text
        
        # Проверяем, находится ли пользователь в процессе создания документа
        if user_id in self._user_document_states:
            await self._handle_document_creation(message)
        elif user_state == MenuType.DOCUMENT_TYPES:
            await self.handle_document_type(message)
        else:
            await self.bot.send_message(
                message.chat.id,
                "❌ Неизвестная команда. Используйте меню ниже:",
                reply_markup=self.keyboards.create_reply_keyboard(MenuType.MAIN)
            )
    
    async def _handle_document_creation(self, message: Any) -> None:
        """Обработка процесса создания документа"""
        user_id = message.from_user.id
        text = message.text
        state = self._user_document_states[user_id]
        
        try:
            if state['step'] == 'awaiting_title':
                # Создаем документ с введенным названием
                document = await self.document_service.create_document(
                    user_telegram_id=user_id,
                    title=text,
                    document_type=state['document_type'],
                    content=f"Черновик документа '{text}'\n\nТип: {state['document_type'].value}"
                )
                
                # Очищаем состояние
                del self._user_document_states[user_id]
                
                await self.bot.send_message(
                    message.chat.id,
                    f"✅ **Документ создан!**\n\n"
                    f"📄 **{document.title}**\n"
                    f"📋 Тип: {self._get_document_type_name(document.document_type)}\n"
                    f"🔄 Статус: Черновик\n\n"
                    f"ID документа: `{document.id}`\n\n"
                    f"Вы можете просмотреть свои документы в разделе '📁 Мои документы'",
                    reply_markup=self.keyboards.create_reply_keyboard(MenuType.MAIN)
                )
                
        except Exception as e:
            print(f"❌ Ошибка при создании документа: {e}")
            await self.bot.send_message(
                message.chat.id,
                f"❌ Ошибка при создании документа: {str(e)}",
                reply_markup=self.keyboards.create_reply_keyboard(MenuType.MAIN)
            )
            # Очищаем состояние в случае ошибки
            if user_id in self._user_document_states:
                del self._user_document_states[user_id]
    
    def _get_document_type_name(self, doc_type: str) -> str:
        """Возвращает читаемое название типа документа"""
        type_names = {
            'claim': 'Исковое заявление',
            'contract': 'Договор',
            'complaint': 'Жалоба',
            'motion': 'Ходатайство'
        }
        return type_names.get(doc_type, doc_type)
    
    def _get_status_name(self, status: str) -> str:
        """Возвращает читаемое название статуса"""
        status_names = {
            'draft': 'Черновик',
            'in_progress': 'В работе',
            'completed': 'Завершен',
            'archived': 'В архиве'
        }
        return status_names.get(status, status)
