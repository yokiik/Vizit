"""Сервис управления заданиями"""
from typing import List, Optional, Dict
from datetime import datetime

from domain.task import Task, TaskStatus
from domain.log import LogEntry, LogLevel, LogCategory, create_user_action_log, create_error_log
from repository.interfaces import TaskRepository, LogRepository, ReferencesRepository, SettingsRepository
from domain.references import ReferenceType


class TaskService:
    """Сервис для работы с заданиями"""
    
    def __init__(
        self,
        task_repo: TaskRepository,
        log_repo: LogRepository,
        ref_repo: ReferencesRepository,
        settings_repo: SettingsRepository
    ):
        self.task_repo = task_repo
        self.log_repo = log_repo
        self.ref_repo = ref_repo
        self.settings_repo = settings_repo
    
    def create_task(self, task: Task) -> None:
        """Создает новое задание"""
        # Валидация
        error_msg = self._validate_task(task)
        if error_msg:
            self._log_error("Ошибка валидации нового задания", Exception(error_msg))
            raise ValueError(f"Валидация задания не пройдена: {error_msg}")
        
        # Устанавливаем значения по умолчанию если нужно
        if task.count_try == 0 or task.delay_try == 0:
            settings = self.settings_repo.get()
            if task.count_try == 0:
                task.count_try = settings.default_execution_attempts
            if task.delay_try == 0:
                task.delay_try = settings.default_delay_try
        
        # Сохраняем
        self.task_repo.save(task)
        
        self._log_user_action(
            f"Создано новое задание: {task.type_task}",
            f"ID: {task.id}, Дата: {task.date}, Слот: {task.time_slot}"
        )
    
    def update_task(self, task: Task) -> None:
        """Обновляет задание"""
        existing_task = self.task_repo.get_by_id(task.id)
        if not existing_task:
            raise ValueError(f"Задание не найдено: {task.id}")
        
        # Валидация
        error_msg = self._validate_task(task)
        if error_msg:
            self._log_error("Ошибка валидации при обновлении задания", Exception(error_msg))
            raise ValueError(f"Валидация задания не пройдена: {error_msg}")
        
        task.created_at = existing_task.created_at
        task.updated_at = datetime.now()
        
        self.task_repo.save(task)
        
        self._log_user_action(
            f"Обновлено задание: {task.type_task}",
            f"ID: {task.id}"
        )
    
    def delete_task(self, task_id: str) -> None:
        """Удаляет задание"""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"Задание не найдено: {task_id}")
        
        self.task_repo.delete(task_id)
        
        self._log_user_action(
            f"Удалено задание: {task.type_task}",
            f"ID: {task_id}"
        )
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Получает задание по ID"""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"Задание не найдено: {task_id}")
        return task
    
    def get_all_tasks(self) -> List[Task]:
        """Получает все задания"""
        try:
            return self.task_repo.get_all()
        except Exception as e:
            self._log_error("Ошибка получения списка заданий", e)
            raise ValueError(f"Не удалось получить список заданий: {e}")
    
    def get_active_tasks_in_order(self) -> List[Task]:
        """Получает активные задания в порядке выполнения"""
        try:
            return self.task_repo.get_active_tasks_in_order()
        except Exception as e:
            self._log_error("Ошибка получения активных заданий", e)
            raise ValueError(f"Не удалось получить активные задания: {e}")
    
    def toggle_task_status(self, task_id: str) -> None:
        """Переключает статус активности задания"""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"Задание не найдено: {task_id}")
        
        task.in_work = not task.in_work
        task.updated_at = datetime.now()
        
        self.task_repo.save(task)
        
        status = "активировано" if task.in_work else "деактивировано"
        self._log_user_action(
            f"Задание {status}",
            f"ID: {task_id}, Тип: {task.type_task}"
        )
    
    def reorder_tasks(self, task_positions: Dict[str, int]) -> None:
        """Изменяет порядок заданий"""
        try:
            self.task_repo.update_positions(task_positions)
            self._log_user_action(
                "Изменен порядок выполнения заданий",
                f"Обновлено позиций: {len(task_positions)}"
            )
        except Exception as e:
            self._log_error("Ошибка изменения порядка заданий", e)
            raise ValueError(f"Не удалось изменить порядок заданий: {e}")
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Получает задания по статусу"""
        try:
            return self.task_repo.get_by_status(status)
        except Exception as e:
            raise ValueError(f"Не удалось получить задания по статусу: {e}")
    
    def start_task_execution(self) -> List[Task]:
        """Запускает выполнение заданий"""
        active_tasks = self.get_active_tasks_in_order()
        
        if not active_tasks:
            self._log_info("Нет активных заданий для выполнения", "")
            return []
        
        for task in active_tasks:
            if task.status == TaskStatus.WAITING:
                task.status = TaskStatus.IN_WORK
                task.updated_at = datetime.now()
                
                try:
                    self.task_repo.save(task)
                except Exception as e:
                    self._log_error(f"Ошибка обновления статуса задания {task.id}", e)
                    continue
        
        self._log_user_action(
            "Запущено выполнение заданий",
            f"Активных заданий: {len(active_tasks)}"
        )
        
        return active_tasks
    
    def stop_task_execution(self) -> None:
        """Останавливает выполнение заданий"""
        working_tasks = self.get_tasks_by_status(TaskStatus.IN_WORK)
        
        for task in working_tasks:
            task.status = TaskStatus.WAITING
            task.updated_at = datetime.now()
            
            try:
                self.task_repo.save(task)
            except Exception as e:
                self._log_error(f"Ошибка остановки задания {task.id}", e)
                continue
        
        self._log_user_action(
            "Остановлено выполнение заданий",
            f"Остановлено заданий: {len(working_tasks)}"
        )
    
    def update_task_status(self, task_id: str, status: str) -> None:
        """Обновляет статус задания"""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"Задание не найдено: {task_id}")
        
        old_status = task.status
        task.set_status(status)
        
        try:
            self.task_repo.save(task)
            self._log_info(f"Статус задания изменен: {old_status} -> {status}", task_id)
        except Exception as e:
            self._log_error("Ошибка обновления статуса задания", e)
            raise ValueError(f"Не удалось обновить статус задания: {e}")
    
    def decrement_task_tries(self, task_id: str) -> None:
        """Уменьшает количество попыток"""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"Задание не найдено: {task_id}")
        
        task.decrement_tries()
        
        try:
            self.task_repo.save(task)
            self._log_info(f"Осталось попыток: {task.count_try}", task_id)
        except Exception as e:
            self._log_error("Ошибка обновления количества попыток", e)
            raise ValueError(f"Не удалось обновить количество попыток: {e}")
    
    def _validate_task(self, task: Task) -> Optional[str]:
        """Валидирует задание"""
        if not task:
            return "Задание не может быть пустым"
        
        if not task.type_task:
            return "Тип задания обязателен"
        
        if not task.date:
            return "Дата задания обязательна"
        
        if not task.time_slot:
            return "Временной слот обязателен"
        
        if not task.num_auto:
            return "Номер автомобиля обязателен"
        
        if not task.driver:
            return "Водитель обязателен"
        
        # Валидация через справочники
        error = self._validate_reference_value(ReferenceType.CAR_NUMBER, task.num_auto)
        if error:
            return f"Неверный номер автомобиля: {error}"
        
        error = self._validate_reference_value(ReferenceType.DRIVER, task.driver)
        if error:
            return f"Неверный водитель: {error}"
        
        error = self._validate_reference_value(ReferenceType.TIME_SLOT, task.time_slot)
        if error:
            return f"Неверный временной слот: {error}"
        
        error = self._validate_reference_value(ReferenceType.OPERATION, task.type_task)
        if error:
            return f"Неверный тип операции: {error}"
        
        if task.status:
            error = self._validate_reference_value(ReferenceType.STATUS, task.status)
            if error:
                return f"Неверный статус: {error}"
        
        return None
    
    def _validate_reference_value(self, ref_type: ReferenceType, value: str) -> Optional[str]:
        """Валидирует значение через справочник"""
        try:
            items = self.ref_repo.get_active_items(ref_type)
        except Exception as e:
            return f"Ошибка получения справочника {ref_type}: {e}"
        
        if not items:
            return f"Справочник {ref_type} пуст, добавьте значения через интерфейс"
        
        for item in items:
            if item.value == value:
                return None
        
        available_values = ", ".join([f"'{item.value}'" for item in items])
        return f"Значение '{value}' не найдено в справочнике {ref_type}. Доступные значения: {available_values}"
    
    def _log_user_action(self, message: str, details: str = ""):
        """Логирует действие пользователя"""
        entry = create_user_action_log(message, details)
        self.log_repo.save(entry)
    
    def _log_info(self, message: str, task_id: str = ""):
        """Логирует информационное сообщение"""
        entry = LogEntry(
            level=LogLevel.INFO,
            category=LogCategory.TASK_EXECUTION,
            message=message,
            task_id=task_id
        )
        self.log_repo.save(entry)
    
    def _log_error(self, message: str, error: Exception):
        """Логирует ошибку"""
        entry = create_error_log(LogCategory.TASK_EXECUTION, message, error)
        self.log_repo.save(entry)

