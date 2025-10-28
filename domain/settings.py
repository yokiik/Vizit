"""Модели настроек"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Settings:
    """Настройки системы"""
    site_url: str = "https://www.rlisystems.ru/conterra/"
    login: str = ""
    password: str = ""
    refresh_interval: int = 30  # секунды
    connection_status: bool = False
    last_connection_test: Optional[datetime] = None
    default_execution_attempts: int = 60  # попытки
    default_delay_try: int = 60  # секунды
    element_timeout: int = 10  # секунды
    use_headless: bool = False
    save_credentials: bool = False
    browser_width: int = 1280
    browser_height: int = 720
    browser_path: str = ""
    slot_check_attempts: int = 10  # попытки проверки слота
    slot_check_interval: int = 5  # секунды между попытками
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Преобразует объект в словарь для JSON"""
        return {
            "site_url": self.site_url,
            "login": self.login,
            "password": self.password,
            "refresh_interval": self.refresh_interval,
            "connection_status": self.connection_status,
            "last_connection_test": self.last_connection_test.isoformat() if self.last_connection_test else None,
            "default_execution_attempts": self.default_execution_attempts,
            "default_delay_try": self.default_delay_try,
            "element_timeout": self.element_timeout,
            "use_headless": self.use_headless,
            "save_credentials": self.save_credentials,
            "browser_width": self.browser_width,
            "browser_height": self.browser_height,
            "browser_path": self.browser_path,
            "slot_check_attempts": self.slot_check_attempts,
            "slot_check_interval": self.slot_check_interval,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Settings':
        """Создает объект из словаря"""
        settings = cls(
            site_url=data.get('site_url', "https://www.rlisystems.ru/conterra/"),
            login=data.get('login', ''),
            password=data.get('password', ''),
            refresh_interval=data.get('refresh_interval', 30),
            connection_status=data.get('connection_status', False),
            default_execution_attempts=data.get('default_execution_attempts', 60),
            default_delay_try=data.get('default_delay_try', 60),
            element_timeout=data.get('element_timeout', 10),
            use_headless=data.get('use_headless', False),
            save_credentials=data.get('save_credentials', False),
            browser_width=data.get('browser_width', 1280),
            browser_height=data.get('browser_height', 720),
            browser_path=data.get('browser_path', ''),
            slot_check_attempts=data.get('slot_check_attempts', 10),
            slot_check_interval=data.get('slot_check_interval', 5)
        )
        
        # Парсинг дат
        if 'last_connection_test' in data and data['last_connection_test']:
            if isinstance(data['last_connection_test'], str):
                settings.last_connection_test = datetime.fromisoformat(data['last_connection_test'])
                
        if 'created_at' in data:
            if isinstance(data['created_at'], str):
                settings.created_at = datetime.fromisoformat(data['created_at'])
                
        if 'updated_at' in data:
            if isinstance(data['updated_at'], str):
                settings.updated_at = datetime.fromisoformat(data['updated_at'])
        
        return settings

    def is_valid(self) -> bool:
        """Проверяет валидность настроек"""
        return bool(
            self.site_url and
            self.login and
            self.password and
            self.refresh_interval > 0 and
            self.default_execution_attempts > 0 and
            self.element_timeout > 0
        )

    def can_test_connection(self) -> bool:
        """Проверяет возможность тестирования подключения"""
        return bool(self.site_url and self.login and self.password)

    def update_connection_status(self, status: bool, message: str = ""):
        """Обновляет статус подключения"""
        self.connection_status = status
        self.last_connection_test = datetime.now()
        self.updated_at = datetime.now()

    def update(self, new_settings: 'Settings'):
        """Обновляет настройки из другого объекта"""
        self.site_url = new_settings.site_url
        self.login = new_settings.login
        self.password = new_settings.password
        self.refresh_interval = new_settings.refresh_interval
        self.default_execution_attempts = new_settings.default_execution_attempts
        self.default_delay_try = new_settings.default_delay_try
        self.element_timeout = new_settings.element_timeout
        self.use_headless = new_settings.use_headless
        self.save_credentials = new_settings.save_credentials
        self.browser_width = new_settings.browser_width
        self.browser_height = new_settings.browser_height
        self.browser_path = new_settings.browser_path
        self.slot_check_attempts = new_settings.slot_check_attempts
        self.slot_check_interval = new_settings.slot_check_interval
        self.updated_at = datetime.now()


@dataclass
class ConnectionTestResult:
    """Результат теста подключения"""
    success: bool
    message: str
    error: str = ""
    duration: int = 0  # миллисекунды
    tested_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Преобразует объект в словарь"""
        return {
            "success": self.success,
            "message": self.message,
            "error": self.error,
            "duration": self.duration,
            "tested_at": self.tested_at.isoformat()
        }

