from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )

    # PostgreSQL настройки
    PG_HOST: str = 'localhost'
    PG_PORT: int = 5432
    PG_USER: str = 'postgres'
    PG_PASSWORD: str = 'postgres'
    PG_DATABASE: str = 'avito_merch'

    # Connection Pool настройки для высоконагруженной системы
    # При RPS 1000 и времени ответа ~50ms
    # Среднее время удержания соединения: ~50ms
    # Теоретический минимум соединений: (1000 RPS * 0.05s) = 50 соединений
    # С учетом пиковых нагрузок и запаса: 50 * 2 = 100 соединений

    # Размер пула соединений (постоянно открытые соединения)
    DB_POOL_SIZE: int = 100

    # Максимальное количество дополнительных соединений сверх pool_size при пиках
    DB_MAX_OVERFLOW: int = 50

    # Таймаут ожидания свободного соединения из пула (секунды)
    DB_POOL_TIMEOUT: int = 10

    # Время жизни соединения в пуле (секунды) - защита от dead connections
    DB_POOL_RECYCLE: int = 3600  # 1 час

    # Проверка соединения перед использованием
    DB_POOL_PRE_PING: bool = True

    # Statement timeout для защиты от долгих запросов (миллисекунды)
    DB_STATEMENT_TIMEOUT: int = 5000  # 5 секунд

    # Command timeout для защиты от зависших операций (секунды)
    DB_COMMAND_TIMEOUT: int = 30

    # Эхо SQL запросов (только для разработки!)
    DB_ECHO: bool = False

    # JWT настройки
    JWT_SECRET_KEY: str = 'your-secret-key-change-in-production-min-32-chars'
    JWT_ALGORITHM: str = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Время жизни токена в минутах

    @property
    def PG_URL(self) -> str:
        """Формирование URL для подключения к PostgreSQL."""
        return (
            f'postgresql+asyncpg://{self.PG_USER}:{self.PG_PASSWORD}'
            f'@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DATABASE}'
        )


settings = Settings()
