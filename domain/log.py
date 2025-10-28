"""Модели логирования"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import random
import string


class LogLevel(str, Enum):
    """Уровни логирования"""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"


class LogCategory(str, Enum):
    """Категории логов"""
    USER_ACTION = "USER_ACTION"
    TASK_EXECUTION = "TASK_EXECUTION"
    BROWSER_AUTOMATION = "BROWSER_AUTOMATION"
    SETTINGS = "SETTINGS"
    REFERENCES = "REFERENCES"
    DATA_STORAGE = "DATA_STORAGE"
    CONNECTION = "CONNECTION"
    SYSTEM = "SYSTEM"


def generate_log_id() -> str:
    """Генерирует уникальный ID для лога"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S.%f")
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    return f"log_{timestamp}_{random_str}"


@dataclass
class LogEntry:
    """Запись лога"""
    id: str = field(default_factory=generate_log_id)
    timestamp: datetime = field(default_factory=datetime.now)
    level: LogLevel = LogLevel.INFO
    category: LogCategory = LogCategory.SYSTEM
    message: str = ""
    details: str = ""
    task_id: str = ""
    user_action: bool = False
    error: str = ""

    def to_dict(self) -> dict:
        """Преобразует объект в словарь"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "category": self.category.value,
            "message": self.message,
            "details": self.details,
            "task_id": self.task_id,
            "user_action": self.user_action,
            "error": self.error
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'LogEntry':
        """Создает объект из словаря"""
        entry = cls(
            id=data.get('id', generate_log_id()),
            level=LogLevel(data.get('level', 'INFO')),
            category=LogCategory(data.get('category', 'SYSTEM')),
            message=data.get('message', ''),
            details=data.get('details', ''),
            task_id=data.get('task_id', ''),
            user_action=data.get('user_action', False),
            error=data.get('error', '')
        )
        
        if 'timestamp' in data:
            if isinstance(data['timestamp'], str):
                entry.timestamp = datetime.fromisoformat(data['timestamp'])
        
        return entry

    def __str__(self) -> str:
        """Строковое представление"""
        timestamp_str = self.timestamp.strftime("%H:%M:%S.%f")[:-3]
        prefix = "[ПОЛЬЗОВАТЕЛЬ] " if self.user_action else ""
        message = f"{timestamp_str} [{self.level.value}] {prefix}{self.message}"
        
        if self.details:
            message += f" - {self.details}"
        
        if self.error:
            message += f" (Ошибка: {self.error})"
        
        if self.task_id:
            message += f" [Задание: {self.task_id}]"
        
        return message

    def get_level_color(self) -> str:
        """Возвращает цвет для уровня лога"""
        colors = {
            LogLevel.TRACE: "#808080",  # Серый
            LogLevel.DEBUG: "#008000",  # Зеленый
            LogLevel.INFO: "#000000",   # Черный
            LogLevel.WARN: "#FFA500",   # Оранжевый
            LogLevel.ERROR: "#FF0000",  # Красный
            LogLevel.FATAL: "#8B0000"   # Темно-красный
        }
        return colors.get(self.level, "#000000")


def create_user_action_log(message: str, details: str = "") -> LogEntry:
    """Создает лог действия пользователя"""
    return LogEntry(
        level=LogLevel.INFO,
        category=LogCategory.USER_ACTION,
        message=message,
        details=details,
        user_action=True
    )


def create_task_log(level: LogLevel, task_id: str, message: str, details: str = "") -> LogEntry:
    """Создает лог задания"""
    return LogEntry(
        level=level,
        category=LogCategory.TASK_EXECUTION,
        message=message,
        details=details,
        task_id=task_id
    )


def create_error_log(category: LogCategory, message: str, error: Exception = None) -> LogEntry:
    """Создает лог ошибки"""
    entry = LogEntry(
        level=LogLevel.ERROR,
        category=category,
        message=message
    )
    if error:
        entry.error = str(error)
        entry.details = f"Ошибка: {error}"
    return entry


def get_category_display_name(category: LogCategory) -> str:
    """Возвращает отображаемое имя категории"""
    names = {
        LogCategory.USER_ACTION: "Действие пользователя",
        LogCategory.TASK_EXECUTION: "Выполнение задания",
        LogCategory.BROWSER_AUTOMATION: "Автоматизация браузера",
        LogCategory.SETTINGS: "Настройки",
        LogCategory.REFERENCES: "Справочники",
        LogCategory.DATA_STORAGE: "Хранилище данных",
        LogCategory.CONNECTION: "Подключение",
        LogCategory.SYSTEM: "Система"
    }
    return names.get(category, str(category))

