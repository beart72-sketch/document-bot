"""Состояния для создания документа"""

from aiogram.fsm.state import State, StatesGroup

class DocumentStates(StatesGroup):
    choosing_type = State()      # Выбор типа: Отчет/Договор/...
    collecting_data = State()    # Сбор данных (ФИО, дата и т.д.)
    confirming = State()         # Подтверждение перед генерацией
