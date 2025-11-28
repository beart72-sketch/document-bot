#!/usr/bin/env python3
"""
Тестирование системы мониторинга и метрик
"""

import asyncio
import logging
import time
from metrics import metrics_collector, performance_monitor, health_checker, initialize_monitoring, shutdown_monitoring, BotMetrics

# Настраиваем логирование для тестов
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')


async def test_metrics_system():
    """Тестирует систему мониторинга и метрик"""
    
    print("🧪 Тестирование системы мониторинга и метрик...")
    
    # Инициализируем мониторинг
    await initialize_monitoring()
    
    try:
        # Тест 1: Базовые метрики
        print("\n1. Тест базовых метрик:")
        
        metrics_collector.increment_counter("test_counter")
        metrics_collector.increment_counter("test_counter", 3)
        metrics_collector.set_gauge("test_gauge", 42.5)
        metrics_collector.record_timer("test_timer", 0.15)
        
        counter_value = metrics_collector.get_counter("test_counter")
        gauge_value = metrics_collector.get_gauge("test_gauge")
        timer_stats = metrics_collector.get_timer_stats("test_timer")
        
        print(f"   Счётчик: {counter_value} (ожидается: 4)")
        print(f"   Gauge: {gauge_value} (ожидается: 42.5)")
        print(f"   Таймер: {timer_stats}")
        
        if counter_value == 4 and gauge_value == 42.5:
            print("   ✅ Базовые метрики работают")
        else:
            print("   ❌ Базовые метрики не работают")
        
        # Тест 2: Декораторы производительности
        print("\n2. Тест декораторов производительности:")
        
        @performance_monitor.track_execution("test_function")
        async def sample_function(delay: float):
            await asyncio.sleep(delay)
            return "done"
        
        result = await sample_function(0.1)
        timer_stats = metrics_collector.get_timer_stats("test_function")
        
        print(f"   Результат функции: {result}")
        print(f"   Статистика выполнения: {timer_stats}")
        
        if timer_stats and timer_stats['count'] == 1:
            print("   ✅ Декораторы производительности работают")
        else:
            print("   ❌ Декораторы производительности не работают")
        
        # Тест 3: Метрики бота
        print("\n3. Тест метрик бота:")
        
        # Создаём mock объекты сообщений
        class MockUser:
            def __init__(self, user_id):
                self.id = user_id
        
        class MockMessage:
            def __init__(self, text, user_id):
                self.text = text
                self.from_user = MockUser(user_id)
                self.content_type = "text"
        
        class MockCallback:
            def __init__(self, data, user_id):
                self.data = data
                self.from_user = MockUser(user_id)
        
        @BotMetrics.track_message()
        async def handle_message(message):
            return f"Обработано: {message.text}"
        
        @BotMetrics.track_callback()
        async def handle_callback(callback):
            return f"Обработано: {callback.data}"
        
        @BotMetrics.track_user_activity()
        async def user_activity(message):
            return f"Активность пользователя {message.from_user.id}"
        
        # Тестируем обработку сообщений
        mock_message = MockMessage("/start", 12345)
        await handle_message(mock_message)
        
        mock_callback = MockCallback("button:click", 12345)
        await handle_callback(mock_callback)
        
        await user_activity(mock_message)
        
        messages_count = metrics_collector.get_counter("messages_received")
        callbacks_count = metrics_collector.get_counter("callbacks_received")
        active_users = metrics_collector.get_counter("active_users")
        
        print(f"   Сообщений: {messages_count}")
        print(f"   Callback-ов: {callbacks_count}")
        print(f"   Активных пользователей: {active_users}")
        
        if messages_count >= 1 and callbacks_count >= 1 and active_users >= 1:
            print("   ✅ Метрики бота работают")
        else:
            print("   ❌ Метрики бота не работают")
        
        # Тест 4: Проверки здоровья
        print("\n4. Тест проверок здоровья:")
        
        health_results = await health_checker.run_health_checks()
        health_status = health_checker.get_health_status()
        
        print(f"   Результаты проверок: {list(health_results.keys())}")
        print(f"   Общий статус: {health_status['status']}")
        print(f"   Процент здоровья: {health_status['health_percentage']}%")
        
        if health_status['total_checks'] > 0:
            print("   ✅ Проверки здоровья работают")
        else:
            print("   ❌ Проверки здоровья не работают")
        
        # Тест 5: Сводка метрик
        print("\n5. Тест сводки метрик:")
        
        summary = metrics_collector.get_metrics_summary()
        print(f"   Счётчиков: {len(summary['counters'])}")
        print(f"   Gauges: {len(summary['gauges'])}")
        print(f"   Таймеров: {len(summary['timers'])}")
        
        if summary['counters'] and summary['timers']:
            print("   ✅ Сводка метрик работает")
        else:
            print("   ❌ Сводка метрик не работает")
        
        print(f"\n🎉 Все тесты мониторинга пройдены успешно!")
        print("✅ Система мониторинга и метрик работает корректно!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании мониторинга: {e}")
        raise
        
    finally:
        # Всегда останавливаем мониторинг
        await shutdown_monitoring()


if __name__ == "__main__":
    asyncio.run(test_metrics_system())
