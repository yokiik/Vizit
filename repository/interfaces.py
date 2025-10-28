"""Интерфейсы репозиториев"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from domain.task import Task
from domain.settings import Settings
from domain.references import References, ReferenceItem, ReferenceType
from domain.log import LogEntry, LogLevel


class TaskRepository(ABC):
    """Интерфейс репозитория заданий"""
    
    @abstractmethod
    def save(self, task: Task) -> None:
        """Сохраняет задание"""
        pass
    
    @abstractmethod
    def get_by_id(self, task_id: str) -> Optional[Task]:
        """Получает задание по ID"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Task]:
        """Получает все задания"""
        pass
    
    @abstractmethod
    def delete(self, task_id: str) -> None:
        """Удаляет задание"""
        pass
    
    @abstractmethod
    def update_positions(self, task_positions: Dict[str, int]) -> None:
        """Обновляет позиции заданий"""
        pass
    
    @abstractmethod
    def get_by_status(self, status: str) -> List[Task]:
        """Получает задания по статусу"""
        pass
    
    @abstractmethod
    def get_active_tasks_in_order(self) -> List[Task]:
        """Получает активные задания в порядке выполнения"""
        pass


class SettingsRepository(ABC):
    """Интерфейс репозитория настроек"""
    
    @abstractmethod
    def save(self, settings: Settings) -> None:
        """Сохраняет настройки"""
        pass
    
    @abstractmethod
    def get(self) -> Settings:
        """Получает настройки"""
        pass
    
    @abstractmethod
    def update(self, settings: Settings) -> None:
        """Обновляет настройки"""
        pass
    
    @abstractmethod
    def exists(self) -> bool:
        """Проверяет существование настроек"""
        pass


class ReferencesRepository(ABC):
    """Интерфейс репозитория справочников"""
    
    @abstractmethod
    def save(self, references: References) -> None:
        """Сохраняет справочники"""
        pass
    
    @abstractmethod
    def get(self) -> References:
        """Получает справочники"""
        pass
    
    @abstractmethod
    def update(self, references: References) -> None:
        """Обновляет справочники"""
        pass
    
    @abstractmethod
    def add_item(self, ref_type: ReferenceType, value: str, description: str = "") -> ReferenceItem:
        """Добавляет элемент в справочник"""
        pass
    
    @abstractmethod
    def remove_item(self, ref_type: ReferenceType, item_id: str) -> None:
        """Удаляет элемент из справочника"""
        pass
    
    @abstractmethod
    def get_active_items(self, ref_type: ReferenceType) -> List[ReferenceItem]:
        """Получает активные элементы справочника"""
        pass


class LogRepository(ABC):
    """Интерфейс репозитория логов"""
    
    @abstractmethod
    def save(self, entry: LogEntry) -> None:
        """Сохраняет запись лога"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[LogEntry]:
        """Получает все логи"""
        pass
    
    @abstractmethod
    def get_by_date_range(self, from_date: str, to_date: str) -> List[LogEntry]:
        """Получает логи за период"""
        pass
    
    @abstractmethod
    def get_by_level(self, level: LogLevel) -> List[LogEntry]:
        """Получает логи по уровню"""
        pass
    
    @abstractmethod
    def get_user_actions(self) -> List[LogEntry]:
        """Получает логи действий пользователя"""
        pass
    
    @abstractmethod
    def get_task_logs(self, task_id: str) -> List[LogEntry]:
        """Получает логи задания"""
        pass
    
    @abstractmethod
    def delete_old_logs(self, days_to_keep: int) -> None:
        """Удаляет старые логи"""
        pass
    
    @abstractmethod
    def get_latest(self, count: int) -> List[LogEntry]:
        """Получает последние N записей"""
        pass
    
    @abstractmethod
    def search(self, query: str) -> List[LogEntry]:
        """Поиск в логах"""
        pass


class DataManager(ABC):
    """Интерфейс менеджера данных"""
    
    @abstractmethod
    def initialize(self) -> None:
        """Инициализирует хранилище"""
        pass
    
    @abstractmethod
    def get_tasks(self) -> TaskRepository:
        """Возвращает репозиторий заданий"""
        pass
    
    @abstractmethod
    def get_settings(self) -> SettingsRepository:
        """Возвращает репозиторий настроек"""
        pass
    
    @abstractmethod
    def get_references(self) -> ReferencesRepository:
        """Возвращает репозиторий справочников"""
        pass
    
    @abstractmethod
    def get_logs(self) -> LogRepository:
        """Возвращает репозиторий логов"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Закрывает соединение с хранилищем"""
        pass
    
    @abstractmethod
    def is_healthy(self) -> bool:
        """Проверяет здоровье хранилища"""
        pass
    
    @abstractmethod
    def backup(self, backup_path: str) -> None:
        """Создает резервную копию"""
        pass
    
    @abstractmethod
    def restore(self, backup_path: str) -> None:
        """Восстанавливает из резервной копии"""
        pass

