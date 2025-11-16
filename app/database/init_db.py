"""Скрипт для инициализации базы данных."""

import asyncio

from sqlalchemy import text

from app.database.base import async_engine, session_factory
from app.database.models import Base, Employee, Merch
from app.utils.auth import get_password_hash


async def init_db() -> None:
    """Создание таблиц и начальных данных."""
    print('Создание таблиц...')

    # Создание всех таблиц
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    print('✓ Таблицы созданы')

    # Добавление тестового сотрудника
    async with session_factory() as session:
        print('\nДобавление тестового сотрудника...')

        test_employee = Employee(
            name='Тестовый Пользователь',
            email='test@avito.ru',
            hashed_password=get_password_hash('password123'),
            balance=1000,
        )
        session.add(test_employee)

        print('✓ Тестовый сотрудник добавлен')
        print('  Email: test@avito.ru')
        print('  Password: password123')
        print('  Balance: 1000 монет')

        # Добавление товаров мерча
        print('\nДобавление товаров мерча...')

        merch_items = [
            Merch(name='t-shirt', price=80),
            Merch(name='cup', price=20),
            Merch(name='book', price=50),
            Merch(name='pen', price=10),
            Merch(name='powerbank', price=200),
            Merch(name='hoody', price=300),
            Merch(name='umbrella', price=200),
            Merch(name='socks', price=10),
            Merch(name='wallet', price=50),
            Merch(name='pink-hoody', price=500),
        ]

        session.add_all(merch_items)
        await session.commit()

        print(f'✓ Добавлено {len(merch_items)} товаров мерча')

        # Вывод списка товаров
        print('\nСписок товаров:')
        for item in merch_items:
            print(f'  - {item.name}: {item.price} монет')

    print('\n✅ Инициализация БД завершена!')


async def check_connection() -> None:
    """Проверка подключения к БД."""
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
        print('✓ Подключение к PostgreSQL успешно')
        return True
    except Exception as e:
        print(f'✗ Ошибка подключения к PostgreSQL: {e}')
        return False


if __name__ == '__main__':
    print('=== Инициализация базы данных ===\n')

    # Проверка подключения
    connected = asyncio.run(check_connection())

    if connected:
        # Инициализация
        asyncio.run(init_db())
    else:
        print('\n⚠️  Убедитесь, что PostgreSQL запущен и настройки подключения в .env корректны')
