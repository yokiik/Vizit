"""JSON реализация репозиториев"""
import json
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from threading import Lock
from typing import List, Optional, Dict

from domain.task import Task
from domain.settings import Settings
from domain.references import References, ReferenceItem, ReferenceType
from domain.log import LogEntry, LogLevel
from .interfaces import (
    TaskRepository, SettingsRepository, ReferencesRepository, 
    LogRepository, DataManager
)


class JSONTaskRepository(TaskRepository):
    """JSON репозиторий заданий"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.file_name = os.path.join(data_dir, "tasks.json")
        self.lock = Lock()
    
    def initialize(self) -> None:
        """Инициализация"""
        if not os.path.exists(self.file_name):
            self._save_to_file([])
    
    def save(self, task: Task) -> None:
        """Сохраняет задание"""
        with self.lock:
            tasks = self._load_from_file()
            found = False
            
            for i, existing_task in enumerate(tasks):
                if existing_task.id == task.id:
                    tasks[i] = task
                    found = True
                    break
            
            if not found:
                # Определяем максимальную позицию
                max_position = max([t.position for t in tasks], default=0)
                task.position = max_position + 1
                tasks.append(task)
            
            self._save_to_file(tasks)
    
    def get_by_id(self, task_id: str) -> Optional[Task]:
        """Получает задание по ID"""
        tasks = self._load_from_file()
        for task in tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_all(self) -> List[Task]:
        """Получает все задания"""
        tasks = self._load_from_file()
        tasks.sort(key=lambda t: t.position)
        return tasks
    
    def delete(self, task_id: str) -> None:
        """Удаляет задание"""
        with self.lock:
            tasks = self._load_from_file()
            tasks = [t for t in tasks if t.id != task_id]
            self._save_to_file(tasks)
    
    def update_positions(self, task_positions: Dict[str, int]) -> None:
        """Обновляет позиции заданий"""
        with self.lock:
            tasks = self._load_from_file()
            for task in tasks:
                if task.id in task_positions:
                    task.position = task_positions[task.id]
                    task.updated_at = datetime.now()
            self._save_to_file(tasks)
    
    def get_by_status(self, status: str) -> List[Task]:
        """Получает задания по статусу"""
        tasks = self.get_all()
        return [t for t in tasks if t.status == status]
    
    def get_active_tasks_in_order(self) -> List[Task]:
        """Получает активные задания в порядке выполнения"""
        tasks = self.get_all()
        return [t for t in tasks if t.in_work]
    
    def _save_to_file(self, tasks: List[Task]) -> None:
        """Сохраняет задания в файл"""
        data = [task.to_dict() for task in tasks]
        with open(self.file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_from_file(self) -> List[Task]:
        """Загружает задания из файла"""
        if not os.path.exists(self.file_name):
            return []
        
        try:
            with open(self.file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Task.from_dict(item) for item in data]
        except Exception as e:
            print(f"Ошибка чтения файла заданий: {e}")
            return []


class JSONSettingsRepository(SettingsRepository):
    """JSON репозиторий настроек"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.file_name = os.path.join(data_dir, "settings.json")
        self.lock = Lock()
    
    def initialize(self) -> None:
        """Инициализация"""
        if not os.path.exists(self.file_name):
            default_settings = Settings()
            self._save_to_file(default_settings)
    
    def save(self, settings: Settings) -> None:
        """Сохраняет настройки"""
        with self.lock:
            self._save_to_file(settings)
    
    def get(self) -> Settings:
        """Получает настройки"""
        return self._load_from_file()
    
    def update(self, settings: Settings) -> None:
        """Обновляет настройки"""
        self.save(settings)
    
    def exists(self) -> bool:
        """Проверяет существование настроек"""
        return os.path.exists(self.file_name)
    
    def _save_to_file(self, settings: Settings) -> None:
        """Сохраняет настройки в файл"""
        data = settings.to_dict()
        with open(self.file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_from_file(self) -> Settings:
        """Загружает настройки из файла"""
        if not os.path.exists(self.file_name):
            return Settings()
        
        try:
            with open(self.file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Settings.from_dict(data)
        except Exception as e:
            print(f"Ошибка чтения файла настроек: {e}")
            return Settings()


class JSONReferencesRepository(ReferencesRepository):
    """JSON репозиторий справочников"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.file_name = os.path.join(data_dir, "references.json")
        self.lock = Lock()
    
    def initialize(self) -> None:
        """Инициализация"""
        if not os.path.exists(self.file_name):
            default_refs = References()
            self._save_to_file(default_refs)
        else:
            self._migrate_references()
    
    def save(self, references: References) -> None:
        """Сохраняет справочники"""
        with self.lock:
            self._save_to_file(references)
    
    def get(self) -> References:
        """Получает справочники"""
        return self._load_from_file()
    
    def update(self, references: References) -> None:
        """Обновляет справочники"""
        self.save(references)
    
    def add_item(self, ref_type: ReferenceType, value: str, description: str = "") -> ReferenceItem:
        """Добавляет элемент в справочник"""
        with self.lock:
            references = self._load_from_file()
            item = references.add_item(ref_type, value, description)
            self._save_to_file(references)
            return item
    
    def remove_item(self, ref_type: ReferenceType, item_id: str) -> None:
        """Удаляет элемент из справочника"""
        with self.lock:
            references = self._load_from_file()
            if not references.remove_item(ref_type, item_id):
                raise ValueError(f"Элемент {item_id} не найден в справочнике {ref_type}")
            self._save_to_file(references)
    
    def get_active_items(self, ref_type: ReferenceType) -> List[ReferenceItem]:
        """Получает активные элементы справочника"""
        references = self.get()
        return references.get_active_items(ref_type)
    
    def _migrate_references(self) -> None:
        """Миграция справочников"""
        with self.lock:
            existing_refs = self._load_from_file()
            default_refs = References()
            updated = False
            
            # Проверяем и дополняем каждый справочник
            if not existing_refs.operation_types and default_refs.operation_types:
                existing_refs.operation_types = default_refs.operation_types
                updated = True
            
            if not existing_refs.statuses and default_refs.statuses:
                existing_refs.statuses = default_refs.statuses
                updated = True
            
            if not existing_refs.car_numbers and default_refs.car_numbers:
                existing_refs.car_numbers = default_refs.car_numbers
                updated = True
            
            if not existing_refs.drivers and default_refs.drivers:
                existing_refs.drivers = default_refs.drivers
                updated = True
            
            if not existing_refs.terminal_contracts and default_refs.terminal_contracts:
                existing_refs.terminal_contracts = default_refs.terminal_contracts
                updated = True
            
            if not existing_refs.time_slots and default_refs.time_slots:
                existing_refs.time_slots = default_refs.time_slots
                updated = True
            
            if updated:
                existing_refs.updated_at = datetime.now()
                self._save_to_file(existing_refs)
    
    def _save_to_file(self, references: References) -> None:
        """Сохраняет справочники в файл"""
        data = references.to_dict()
        with open(self.file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_from_file(self) -> References:
        """Загружает справочники из файла"""
        if not os.path.exists(self.file_name):
            return References()
        
        try:
            with open(self.file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return References.from_dict(data)
        except Exception as e:
            print(f"Ошибка чтения файла справочников: {e}")
            return References()


class JSONLogRepository(LogRepository):
    """JSON репозиторий логов"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.file_name = os.path.join(data_dir, "logs.json")
        self.lock = Lock()
    
    def initialize(self) -> None:
        """Инициализация"""
        if not os.path.exists(self.file_name):
            self._save_to_file([])
    
    def save(self, entry: LogEntry) -> None:
        """Сохраняет запись лога"""
        with self.lock:
            logs = self._load_from_file()
            logs.append(entry)
            self._save_to_file(logs)
    
    def get_all(self) -> List[LogEntry]:
        """Получает все логи"""
        logs = self._load_from_file()
        logs.sort(key=lambda l: l.timestamp)
        return logs
    
    def get_by_date_range(self, from_date: str, to_date: str) -> List[LogEntry]:
        """Получает логи за период"""
        logs = self.get_all()
        from_dt = datetime.fromisoformat(from_date)
        to_dt = datetime.fromisoformat(to_date) + timedelta(days=1)
        
        return [log for log in logs if from_dt <= log.timestamp < to_dt]
    
    def get_by_level(self, level: LogLevel) -> List[LogEntry]:
        """Получает логи по уровню"""
        logs = self.get_all()
        return [log for log in logs if log.level == level]
    
    def get_user_actions(self) -> List[LogEntry]:
        """Получает логи действий пользователя"""
        logs = self.get_all()
        return [log for log in logs if log.user_action]
    
    def get_task_logs(self, task_id: str) -> List[LogEntry]:
        """Получает логи задания"""
        logs = self.get_all()
        return [log for log in logs if log.task_id == task_id]
    
    def delete_old_logs(self, days_to_keep: int) -> None:
        """Удаляет старые логи"""
        with self.lock:
            logs = self._load_from_file()
            cutoff_time = datetime.now() - timedelta(days=days_to_keep)
            logs = [log for log in logs if log.timestamp > cutoff_time]
            self._save_to_file(logs)
    
    def get_latest(self, count: int) -> List[LogEntry]:
        """Получает последние N записей"""
        logs = self.get_all()
        return logs[-count:] if len(logs) > count else logs
    
    def search(self, query: str) -> List[LogEntry]:
        """Поиск в логах"""
        logs = self.get_all()
        query_lower = query.lower()
        
        return [
            log for log in logs
            if query_lower in log.message.lower() or
               query_lower in log.details.lower() or
               query_lower in log.error.lower()
        ]
    
    def _save_to_file(self, logs: List[LogEntry]) -> None:
        """Сохраняет логи в файл"""
        data = [log.to_dict() for log in logs]
        with open(self.file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_from_file(self) -> List[LogEntry]:
        """Загружает логи из файла"""
        if not os.path.exists(self.file_name):
            return []
        
        try:
            with open(self.file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [LogEntry.from_dict(item) for item in data]
        except Exception as e:
            print(f"Ошибка чтения файла логов: {e}")
            return []


class JSONDataManager(DataManager):
    """Менеджер данных с JSON хранилищем"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.tasks_repo = JSONTaskRepository(data_dir)
        self.settings_repo = JSONSettingsRepository(data_dir)
        self.references_repo = JSONReferencesRepository(data_dir)
        self.logs_repo = JSONLogRepository(data_dir)
    
    def initialize(self) -> None:
        """Инициализирует хранилище"""
        # Создаем директорию если не существует
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        
        # Инициализируем репозитории
        self.tasks_repo.initialize()
        self.settings_repo.initialize()
        self.references_repo.initialize()
        self.logs_repo.initialize()
        
        print(f"✓ Хранилище данных инициализировано: {self.data_dir}")
    
    def get_tasks(self) -> TaskRepository:
        """Возвращает репозиторий заданий"""
        return self.tasks_repo
    
    def get_settings(self) -> SettingsRepository:
        """Возвращает репозиторий настроек"""
        return self.settings_repo
    
    def get_references(self) -> ReferencesRepository:
        """Возвращает репозиторий справочников"""
        return self.references_repo
    
    def get_logs(self) -> LogRepository:
        """Возвращает репозиторий логов"""
        return self.logs_repo
    
    def close(self) -> None:
        """Закрывает соединение с хранилищем"""
        pass  # JSON не требует закрытия
    
    def is_healthy(self) -> bool:
        """Проверяет здоровье хранилища"""
        if not os.path.exists(self.data_dir):
            return False
        
        # Проверяем возможность записи
        test_file = os.path.join(self.data_dir, "health_check.tmp")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return True
        except Exception:
            return False
    
    def backup(self, backup_path: str) -> None:
        """Создает резервную копию"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(backup_path, f"backup_{timestamp}")
        
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
        
        # Копируем все JSON файлы
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                src = os.path.join(self.data_dir, filename)
                dst = os.path.join(backup_dir, filename)
                shutil.copy2(src, dst)
        
        print(f"✓ Резервная копия создана: {backup_dir}")
    
    def restore(self, backup_path: str) -> None:
        """Восстанавливает из резервной копии"""
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Директория резервной копии не существует: {backup_path}")
        
        # Копируем все JSON файлы обратно
        for filename in os.listdir(backup_path):
            if filename.endswith('.json'):
                src = os.path.join(backup_path, filename)
                dst = os.path.join(self.data_dir, filename)
                shutil.copy2(src, dst)
        
        print(f"✓ Данные восстановлены из: {backup_path}")

