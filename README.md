# Avito PR Service

Сервис для управления Pull Request'ами и командами разработчиков.

## Требования

- Docker
- Docker Compose

## Запуск

```bash
docker-compose up
```

Сервис будет доступен на `http://localhost:8080`

## API Документация

Swagger UI доступен по адресу: `http://localhost:8080/docs`

## Эндпоинты

### Команды

- **POST /team/add** - Создать команду с участниками
- **GET /team/get** - Получить информацию о команде

### Pull Requests

(Будут добавлены согласно OpenAPI спецификации)

## Характеристики

- RPS: 5
- SLI времени ответа: 300 мс  
- SLI успешности: 99.9%
- Объём данных: до 20 команд и до 200 пользователей

## Миграции

Миграции применяются автоматически при запуске контейнера.

## Разработка

```bash
# Установка зависимостей
poetry install

# Запуск локально
python run.py

# Создание миграции
alembic revision --autogenerate -m "description"

# Применение миграций
alembic upgrade head
```
