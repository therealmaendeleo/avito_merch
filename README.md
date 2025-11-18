# Сервис назначения ревьюеров для Pull Request’ов

REST API сервис для автоматического назначения ревьюверов на Pull Request'ы. При создании PR система выбирает до 2 активных участников из команды автора, исключая самого автора. Реализована логика переназначения ревьюверов и идемпотентный merge.

---

## Запуск

```bash
docker-compose up --build
```

Документация API: `http://localhost:8080/docs`

## Коды ошибок

| Код            | Описание                     | HTTP Status |
| -------------- | ---------------------------- | ----------- |
| `TEAM_EXISTS`  | Команда уже существует       | 409         |
| `PR_EXISTS`    | PR с таким ID уже существует | 409         |
| `NOT_FOUND`    | Ресурс не найден             | 404         |
| `PR_MERGED`    | Нельзя изменить после merge  | 409         |
| `NOT_ASSIGNED` | Ревьювер не назначен на PR   | 409         |
| `NO_CANDIDATE` | Нет доступных кандидатов     | 409         |

## Технологический стек

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy (asyncpg)
- **Migrations**: Alembic
- **Deployment**: Docker & Docker Compose
