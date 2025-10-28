"""Модели справочников"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from enum import Enum
import random
import string


class ReferenceType(str, Enum):
    """Типы справочников"""
    OPERATION = "operation_types"
    STATUS = "statuses"
    CAR_NUMBER = "car_numbers"
    DRIVER = "drivers"
    CONTRACT = "terminal_contracts"
    TIME_SLOT = "time_slots"


def generate_reference_id() -> str:
    """Генерирует уникальный ID для справочника"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    return f"ref_{timestamp}_{random_str}"


@dataclass
class ReferenceItem:
    """Элемент справочника"""
    id: str = field(default_factory=generate_reference_id)
    value: str = ""
    description: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Преобразует объект в словарь"""
        return {
            "id": self.id,
            "value": self.value,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ReferenceItem':
        """Создает объект из словаря"""
        item = cls(
            id=data.get('id', generate_reference_id()),
            value=data.get('value', ''),
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
        
        if 'created_at' in data:
            if isinstance(data['created_at'], str):
                item.created_at = datetime.fromisoformat(data['created_at'])
                
        if 'updated_at' in data:
            if isinstance(data['updated_at'], str):
                item.updated_at = datetime.fromisoformat(data['updated_at'])
        
        return item


@dataclass
class References:
    """Справочники системы"""
    operation_types: List[ReferenceItem] = field(default_factory=list)
    statuses: List[ReferenceItem] = field(default_factory=list)
    car_numbers: List[ReferenceItem] = field(default_factory=list)
    drivers: List[ReferenceItem] = field(default_factory=list)
    terminal_contracts: List[ReferenceItem] = field(default_factory=list)
    time_slots: List[ReferenceItem] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Инициализация справочников данными по умолчанию"""
        if not self.operation_types:
            self._init_operation_types()
        if not self.statuses:
            self._init_statuses()
        if not self.time_slots:
            self._init_time_slots()
        if not self.car_numbers:
            self._init_car_numbers()
        if not self.drivers:
            self._init_drivers()
        if not self.terminal_contracts:
            self._init_contracts()

    def _init_operation_types(self):
        """Инициализация типов операций"""
        now = datetime.now()
        self.operation_types = [
            ReferenceItem(id="op_import", value="Ввоз", is_active=True, created_at=now, updated_at=now),
            ReferenceItem(id="op_export", value="Вывоз", is_active=True, created_at=now, updated_at=now)
        ]

    def _init_statuses(self):
        """Инициализация статусов"""
        now = datetime.now()
        self.statuses = [
            ReferenceItem(id="status_new", value="Новый", is_active=True, created_at=now, updated_at=now),
            ReferenceItem(id="status_completed", value="Выполнено", is_active=True, created_at=now, updated_at=now),
            ReferenceItem(id="status_in_work", value="В работе", is_active=True, created_at=now, updated_at=now),
            ReferenceItem(id="status_waiting", value="Ожидает", is_active=True, created_at=now, updated_at=now),
            ReferenceItem(id="status_skipped", value="Пропущен", is_active=True, created_at=now, updated_at=now),
            ReferenceItem(id="status_stopped", value="Остановлен", is_active=True, created_at=now, updated_at=now)
        ]

    def _init_time_slots(self):
        """Инициализация временных слотов"""
        now = datetime.now()
        slots_data = [
            ("ts_0100_0400", "01:00-04:00"),
            ("ts_0430_0730", "04:30-07:30"),
            ("ts_0800_1200", "08:00-12:00"),
            ("ts_1300_1600", "13:00-16:00"),
            ("ts_1630_1930", "16:30-19:30"),
            ("ts_2000_0000", "20:00-00:00")
        ]
        self.time_slots = [
            ReferenceItem(id=item_id, value=value, is_active=True, created_at=now, updated_at=now)
            for item_id, value in slots_data
        ]

    def _init_car_numbers(self):
        """Инициализация госномеров"""
        now = datetime.now()
        self.car_numbers = [
            ReferenceItem(id="car_a001aa78", value="А001АА78", is_active=True, created_at=now, updated_at=now),
            ReferenceItem(id="car_b002bb78", value="В002ВВ78", is_active=True, created_at=now, updated_at=now),
            ReferenceItem(id="car_c003cc78", value="С003СС78", is_active=True, created_at=now, updated_at=now)
        ]

    def _init_drivers(self):
        """Инициализация водителей"""
        now = datetime.now()
        self.drivers = [
            ReferenceItem(id="driver_ivanov", value="Иванов И.И.", is_active=True, created_at=now, updated_at=now),
            ReferenceItem(id="driver_petrov", value="Петров П.П.", is_active=True, created_at=now, updated_at=now),
            ReferenceItem(id="driver_sidorov", value="Сидоров С.С.", is_active=True, created_at=now, updated_at=now)
        ]

    def _init_contracts(self):
        """Инициализация договоров"""
        now = datetime.now()
        self.terminal_contracts = [
            ReferenceItem(id="contract_001", value="Договор №001/2025", 
                         description="Основной договор с терминалом", is_active=True, created_at=now, updated_at=now),
            ReferenceItem(id="contract_002", value="Договор №002/2025", 
                         description="Дополнительный договор", is_active=True, created_at=now, updated_at=now)
        ]

    def to_dict(self) -> dict:
        """Преобразует объект в словарь"""
        return {
            "operation_types": [item.to_dict() for item in self.operation_types],
            "statuses": [item.to_dict() for item in self.statuses],
            "car_numbers": [item.to_dict() for item in self.car_numbers],
            "drivers": [item.to_dict() for item in self.drivers],
            "terminal_contracts": [item.to_dict() for item in self.terminal_contracts],
            "time_slots": [item.to_dict() for item in self.time_slots],
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'References':
        """Создает объект из словаря"""
        refs = cls(
            operation_types=[ReferenceItem.from_dict(item) for item in data.get('operation_types', [])],
            statuses=[ReferenceItem.from_dict(item) for item in data.get('statuses', [])],
            car_numbers=[ReferenceItem.from_dict(item) for item in data.get('car_numbers', [])],
            drivers=[ReferenceItem.from_dict(item) for item in data.get('drivers', [])],
            terminal_contracts=[ReferenceItem.from_dict(item) for item in data.get('terminal_contracts', [])],
            time_slots=[ReferenceItem.from_dict(item) for item in data.get('time_slots', [])]
        )
        
        if 'updated_at' in data:
            if isinstance(data['updated_at'], str):
                refs.updated_at = datetime.fromisoformat(data['updated_at'])
        
        return refs

    def get_active_items(self, ref_type: ReferenceType) -> List[ReferenceItem]:
        """Возвращает активные элементы справочника"""
        items_map = {
            ReferenceType.OPERATION: self.operation_types,
            ReferenceType.STATUS: self.statuses,
            ReferenceType.CAR_NUMBER: self.car_numbers,
            ReferenceType.DRIVER: self.drivers,
            ReferenceType.CONTRACT: self.terminal_contracts,
            ReferenceType.TIME_SLOT: self.time_slots
        }
        items = items_map.get(ref_type, [])
        return [item for item in items if item.is_active]

    def add_item(self, ref_type: ReferenceType, value: str, description: str = "") -> ReferenceItem:
        """Добавляет элемент в справочник"""
        item = ReferenceItem(value=value, description=description)
        
        items_map = {
            ReferenceType.OPERATION: self.operation_types,
            ReferenceType.STATUS: self.statuses,
            ReferenceType.CAR_NUMBER: self.car_numbers,
            ReferenceType.DRIVER: self.drivers,
            ReferenceType.CONTRACT: self.terminal_contracts,
            ReferenceType.TIME_SLOT: self.time_slots
        }
        
        items = items_map.get(ref_type)
        if items is not None:
            items.append(item)
            self.updated_at = datetime.now()
        
        return item

    def remove_item(self, ref_type: ReferenceType, item_id: str) -> bool:
        """Удаляет элемент из справочника"""
        items_map = {
            ReferenceType.OPERATION: self.operation_types,
            ReferenceType.STATUS: self.statuses,
            ReferenceType.CAR_NUMBER: self.car_numbers,
            ReferenceType.DRIVER: self.drivers,
            ReferenceType.CONTRACT: self.terminal_contracts,
            ReferenceType.TIME_SLOT: self.time_slots
        }
        
        items = items_map.get(ref_type)
        if items is not None:
            for i, item in enumerate(items):
                if item.id == item_id:
                    items.pop(i)
                    self.updated_at = datetime.now()
                    return True
        return False

    def has_duplicate_value(self, ref_type: ReferenceType, value: str) -> bool:
        """Проверяет наличие дубликата"""
        items = self.get_active_items(ref_type)
        return any(item.value.lower() == value.lower() for item in items)

    def validate_new_item(self, ref_type: ReferenceType, value: str, description: str = "") -> tuple[bool, str]:
        """Валидирует новый элемент справочника"""
        if not value.strip():
            return False, "Значение не может быть пустым"
        if len(value) > 100:
            return False, "Значение не может быть длиннее 100 символов"
        if len(description) > 255:
            return False, "Описание не может быть длиннее 255 символов"
        if self.has_duplicate_value(ref_type, value):
            return False, f"Запись с таким значением уже существует: {value}"
        return True, ""


def get_reference_type_display_name(ref_type: ReferenceType) -> str:
    """Возвращает отображаемое имя типа справочника"""
    names = {
        ReferenceType.OPERATION: "Тип операции",
        ReferenceType.STATUS: "Статус",
        ReferenceType.CAR_NUMBER: "Госномера автомобилей",
        ReferenceType.DRIVER: "Водитель",
        ReferenceType.CONTRACT: "Договора с терминалом",
        ReferenceType.TIME_SLOT: "Временные слоты"
    }
    return names.get(ref_type, str(ref_type))

