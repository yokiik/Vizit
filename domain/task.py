"""Модели заданий"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import random
import string

# Временные слоты
TIME_SLOTS = [
    "01:00-04:00",
    "04:30-07:30",
    "08:00-12:00",
    "13:00-16:00",
    "16:30-19:30",
    "20:00-00:00",
]


class TaskStatus:
    """Статусы заданий"""
    NEW = "Новый"
    COMPLETED = "Выполнено"
    IN_WORK = "В работе"
    WAITING = "Ожидает"
    SKIPPED = "Пропущен"
    STOPPED = "Остановлен"


class TaskType:
    """Типы заданий"""
    IMPORT = "Ввоз"
    EXPORT = "Вывоз"


def random_string(length: int) -> str:
    """Генерирует случайную строку"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_id() -> str:
    """Генерирует уникальный ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{timestamp}_{random_string(6)}"


@dataclass
class Task:
    """Модель задания"""
    id: str = field(default_factory=generate_id)
    in_work: bool = False
    type_task: str = ""
    status: str = field(default=TaskStatus.NEW)
    date: str = ""
    time_slot: str = ""
    time_cancel: int = 30  # минуты
    count_try: int = 60  # попытки
    delay_try: int = 60  # секунды
    num_auto: str = ""
    driver: str = ""
    place: str = ""
    index_container: str = ""
    number_container: str = ""
    release_order: str = ""
    contract_terminal: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    position: int = 0

    def to_dict(self) -> dict:
        """Преобразует объект в словарь для JSON"""
        return {
            "id": self.id,
            "in_work": self.in_work,
            "type_task": self.type_task,
            "status": self.status,
            "date": self.date,
            "time_slot": self.time_slot,
            "time_cancel": self.time_cancel,
            "count_try": self.count_try,
            "delay_try": self.delay_try,
            "num_auto": self.num_auto,
            "driver": self.driver,
            "place": self.place,
            "index_container": self.index_container,
            "number_container": self.number_container,
            "release_order": self.release_order,
            "contract_terminal": self.contract_terminal,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "position": self.position
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Создает объект из словаря"""
        task = cls(
            id=data.get('id', generate_id()),
            in_work=data.get('in_work', False),
            type_task=data.get('type_task', ''),
            status=data.get('status', TaskStatus.NEW),
            date=data.get('date', ''),
            time_slot=data.get('time_slot', ''),
            time_cancel=data.get('time_cancel', 30),
            count_try=data.get('count_try', 60),
            delay_try=data.get('delay_try', 60),
            num_auto=data.get('num_auto', ''),
            driver=data.get('driver', ''),
            place=data.get('place', ''),
            index_container=data.get('index_container', ''),
            number_container=data.get('number_container', ''),
            release_order=data.get('release_order', ''),
            contract_terminal=data.get('contract_terminal', ''),
            position=data.get('position', 0)
        )
        
        # Парсинг дат
        if 'created_at' in data:
            if isinstance(data['created_at'], str):
                task.created_at = datetime.fromisoformat(data['created_at'])
            elif isinstance(data['created_at'], datetime):
                task.created_at = data['created_at']
                
        if 'updated_at' in data:
            if isinstance(data['updated_at'], str):
                task.updated_at = datetime.fromisoformat(data['updated_at'])
            elif isinstance(data['updated_at'], datetime):
                task.updated_at = data['updated_at']
        
        return task

    def is_valid(self) -> bool:
        """Проверяет валидность задания"""
        return bool(
            self.type_task and
            self.date and
            self.time_slot and
            self.num_auto and
            self.driver
        )

    def can_execute(self) -> bool:
        """Проверяет возможность выполнения задания"""
        return (
            self.in_work and
            self.status == TaskStatus.WAITING and
            self.count_try > 0 and
            self.is_valid()
        )

    def decrement_tries(self):
        """Уменьшает количество попыток"""
        if self.count_try > 0:
            self.count_try -= 1
        self.updated_at = datetime.now()

    def set_status(self, status: str):
        """Устанавливает статус"""
        self.status = status
        self.updated_at = datetime.now()

