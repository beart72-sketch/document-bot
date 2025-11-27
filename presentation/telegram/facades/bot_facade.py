from typing import Dict, Any
from telebot.async_telebot import AsyncTeleBot
from domain.services.menu_service import MenuService
from presentation.telegram.keyboards.main_keyboards import MainKeyboards
from application.services.user_service import UserService
from application.services.document_service import DocumentService
from application.services.subscription_service import SubscriptionService
from domain.entities.document import DocumentType
from domain.entities.menu import MenuType
from domain.entities.subscription import SubscriptionPlan

class BotFacade:
    """Фасад для работы с ботом"""
    
    def __init__(self, bot: AsyncTeleBot, user_service: UserService, 
                 document_service: DocumentService,
                 subscription_service: SubscriptionService,
                 menu_service: MenuService, keyboards: MainKeyboards):
        self.bot = bot
        self.user_service = user_service
        self.document_service = document_service
        self.subscription_service = subscription_service
        self.menu_service = menu_service
        self.keyboards = keyboards
        self._user_document_states: Dict[int, Dict[str, Any]] = {}
    
    async def _ensure_user_exists(self, message: Any) -> Any:
        """Гарантирует что пользователь существует в системе"""
        user_id = message.from_user.id
        user = await self.user_service.get_or_create_user(
            telegram_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        return user
    
    async def handle_start(self, message: Any) -> None:
        """Обработка команды /start"""
        user = await self._ensure_user_exists(message)
        user_id = message.from_user.id
        self.menu_service.set_user_state(user_id, MenuType.MAIN)
        
        print(f"👤 Пользователь: {user.first_name} (ID: {user.telegram_id})")
        
        menu = self.keyboards.create_reply_keyboard(MenuType.MAIN)
        
        await self.bot.send_message(
            message.chat.id,
            f"👋 Добро пожаловать, {user.first_name or 'пользователь'}!\n\n"
            "Я помогу вам создавать юридические документы. "
            "Выберите действие из меню ниже:",
            reply_markup=menu
        )
    
    async def handle_subscription(self, message: Any) -> None:
        """Обработчик управления подпиской"""
        user = await self._ensure_user_exists(message)
        user_id = message.from_user.id
        
        try:
            # Получаем информацию о подписке
            subscription_info = await self.subscription_service.get_subscription_info(user.id)
            
            plan_names = {
                "free": "🆓 Бесплатный",
                "premium": "💎 Премиум", 
                "business": "🏢 Бизнес"
            }
            
            plan_emoji = plan_names.get(subscription_info["plan"], "🆓")
            
            response_text = (
                f"{plan_emoji} **Ваша подписка**\n\n"
                f"📊 **Текущий план:** {subscription_info['plan'].upper()}\n"
                f"🔄 **Статус:** {subscription_info['status']}\n"
                f"📅 **Дней осталось:** {subscription_info['days_remaining']}\n"
                f"⏰ **Действует до:** {subscription_info['end_date'].strftime('%d.%m.%Y')}\n\n"
            )
            
            # Добавляем информацию о лимитах
            features = subscription_info["features"]
            response_text += (
                "📋 **Ваши лимиты:**\n"
                f"• 📄 Документов в месяц: {features.get('documents_per_month', 5)}\n"
                f"• 🤖 AI-запросов: {features.get('ai_requests', 10)}\n"
                f"• 📝 Макс. длина документа: {features.get('max_document_length', 1000)} символов\n\n"
            )
            
            # Добавляем информацию о доступных шаблонах
            templates = features.get('templates_access', ['basic'])
            response_text += f"• 🎨 Доступные шаблоны: {', '.join(templates)}\n\n"
            
            if subscription_info["plan"] == "free":
                response_text += (
                    "💎 **Премиум функции:**\n"
                    "• 📈 Больше документов в месяц\n"
                    "• 🚀 Приоритетная генерация\n" 
                    "• 🎨 Расширенные шаблоны\n"
                    "• 🤖 Больше AI-запросов\n\n"
                    "Нажмите '💎 Премиум' для улучшения подписки!"
                )
            
            await self.bot.send_message(message.chat.id, response_text)
            
        except Exception as e:
            print(f"❌ Ошибка при получении информации о подписке: {e}")
            await self.bot.send_message(
                message.chat.id,
                "❌ Произошла ошибка при загрузке информации о подписке. Попробуйте позже."
            )
    
    async def handle_premium(self, message: Any) -> None:
        """Обработчик премиум подписки"""
        user = await self._ensure_user_exists(message)
        
        premium_text = (
            "💎 **Премиум подписка**\n\n"
            "**Что вы получаете:**\n"
            "• 📈 50 документов в месяц (вместо 5)\n"
            "• 🚀 Приоритетная генерация документов\n"
            "• 🎨 Доступ к премиум шаблонам\n"
            "• 🤖 100 AI-запросов в месяц\n"
            "• 📝 Увеличенная длина документов\n\n"
            
            "🏢 **Бизнес подписка**\n"
            "• 📈 500 документов в месяц\n" 
            "• ⚡ Максимальная скорость\n"
            "• 🎨 Все шаблоны включая бизнес\n"
            "• 🤖 1000 AI-запросов в месяц\n"
            "• 🔧 Персональная поддержка\n\n"
            
            "💰 **Стоимость:**\n"
            "• 💎 Премиум: 299₽/месяц\n"
            "• 🏢 Бизнес: 999₽/месяц\n\n"
            
            "🛒 Для приобретения подписки обратитесь к администратору @admin\n"
            "или используйте команду /payment"
        )
        
        await self.bot.send_message(message.chat.id, premium_text)
    
    async def handle_payment(self, message: Any) -> None:
        """Обработчик оплаты подписки"""
        payment_text = (
            "💳 **Оплата подписки**\n\n"
            "**Доступные способы оплаты:**\n"
            "• 💰 Банковская карта (Visa/MasterCard/Мир)\n"
            "• 🤝 ЮMoney\n"
            "• 📱 СБП (Система быстрых платежей)\n"
            "• 💎 Crypto (USDT, BTC)\n\n"
            
            "**Инструкция по оплате:**\n"
            "1. Выберите желаемый план подписки\n"
            "2. Нажмите кнопку 'Оплатить'\n"
            "3. Следуйте инструкциям платежной системы\n"
            "4. Подписка активируется автоматически\n\n"
            
            "📞 **Поддержка:** @admin\n"
            "⏰ **Время активации:** до 15 минут\n\n"
            
            "⚠️ **Внимание:** Это демо-версия. В реальном боте здесь будет интеграция с платежной системой."
        )
        
        await self.bot.send_message(message.chat.id, payment_text)

    # Остальные методы остаются без изменений...
    async def handle_message(self, message: Any) -> None:
        """Обработка всех сообщений"""
        # Сначала гарантируем что пользователь существует
        await self._ensure_user_exists(message)
        
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
        await self._ensure_user_exists(message)
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
    
    async def handle_my_documents(self, message: Any) -> None:
        """Обработчик моих документов"""
        user = await self._ensure_user_exists(message)
        user_id = message.from_user.id
        
        try:
            # Получаем документы пользователя
            documents_response = await self.document_service.get_user_documents(user.telegram_id)
            
            if documents_response.documents:
                response_text = "📂 **Ваши документы:**\n\n"
                for i, doc in enumerate(documents_response.documents, 1):
                    # Безопасное получение типа документа
                    doc_type = doc.document_type
                    if hasattr(doc_type, 'value'):
                        doc_type = doc_type.value
                    
                    status_emoji = {
                        'draft': '📄',
                        'in_progress': '🔄', 
                        'completed': '✅',
                        'archived': '📦'
                    }.get(doc.status, '📄')
                    
                    response_text += (
                        f"{i}. {status_emoji} **{doc.title}**\n"
                        f"   Тип: {self._get_document_type_name(doc_type)}\n"
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
    
    async def handle_document_type(self, message: Any) -> None:
        """Обработчик выбора типа документа"""
        await self._ensure_user_exists(message)
        user_id = message.from_user.id
        text = message.text
        
        # Определяем тип документа по тексту
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
    
    async def handle_settings(self, message: Any) -> None:
        """Обработчик настроек"""
        await self._ensure_user_exists(message)
        await self.bot.send_message(
            message.chat.id,
            "⚙️ **Настройки**\n\n"
            "Раздел находится в разработке."
        )
    
    async def handle_help(self, message: Any) -> None:
        """Обработчик помощи из меню"""
        await self._ensure_user_exists(message)
        await self.bot.send_message(
            message.chat.id,
            "📖 **Помощь по боту**\n\n"
            "• 📋 Создать документ - создание новых юридических документов\n"
            "• 📂 Мои документы - просмотр созданных документов\n"
            "• 💎 Премиум - информация о подписках\n"
            "• 💳 Подписка - управление вашей подпиской\n"
            "• ⚙️ Настройки - настройки аккаунта\n"
            "• 🆘 Помощь - это сообщение\n\n"
            "Для начала работы используйте меню ниже."
        )
    
    async def handle_back(self, message: Any) -> None:
        """Обработчик кнопки Назад"""
        await self._ensure_user_exists(message)
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
        await self._ensure_user_exists(message)
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
        await self._ensure_user_exists(message)
        user_id = message.from_user.id
        text = message.text
        state = self._user_document_states[user_id]
        
        try:
            if state['step'] == 'awaiting_title':
                # Безопасное получение значения типа документа
                document_type = state['document_type']
                if hasattr(document_type, 'value'):
                    document_type_value = document_type.value
                else:
                    document_type_value = str(document_type)
                
                # Создаем документ с введенным названием
                document = await self.document_service.create_document(
                    user_id=user_id,  # 🔥 ИСПРАВЛЕНО: user_id вместо user_telegram_id
                    title=text,
                    document_type=document_type_value,
                    content=f"Черновик документа '{text}'\n\nТип: {document_type_value}"
                )
                
                # Очищаем состояние
                del self._user_document_states[user_id]
                
                await self.bot.send_message(
                    message.chat.id,
                    f"✅ **Документ создан!**\n\n"
                    f"📄 **{document.title}**\n"
                    f"📋 Тип: {self._get_document_type_name(document_type_value)}\n"
                    f"🔄 Статус: Черновик\n\n"
                    f"ID документа: `{document.id}`\n\n"
                    f"Вы можете просмотреть свои документы в разделе '📂 Мои документы'",
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
