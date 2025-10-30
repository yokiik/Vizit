"""Pydantic модели для FastAPI"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# Модели для заданий
class TaskCreate(BaseModel):
    """Модель для создания задания"""
    type_task: str = Field(..., description="Тип задания")
    status: str = Field(default="Новый", description="Статус")
    date: str = Field(..., description="Дата")
    time_slot: str = Field(..., description="Временной слот")
    num_auto: str = Field(..., description="Номер автомобиля")
    driver: str = Field(..., description="Водитель")
    place: str = Field(default="", description="Место")
    index_container: str = Field(default="", description="Индекс контейнера")
    number_container: str = Field(default="", description="Номер контейнера")
    release_order: str = Field(default="", description="Номер ордера")
    contract_terminal: str = Field(default="", description="Договор с терминалом")
    time_cancel: int = Field(default=30, description="Время отмены (минуты)")
    count_try: int = Field(default=60, description="Количество попыток")
    delay_try: int = Field(default=60, description="Задержка между попытками (секунды)")


class TaskUpdate(BaseModel):
    """Модель для обновления задания"""
    id: str = Field(..., description="ID задания")
    in_work: bool = Field(default=False, description="В работе")
    type_task: str = Field(..., description="Тип задания")
    status: str = Field(..., description="Статус")
    date: str = Field(..., description="Дата")
    time_slot: str = Field(..., description="Временной слот")
    num_auto: str = Field(..., description="Номер автомобиля")
    driver: str = Field(..., description="Водитель")
    place: str = Field(default="", description="Место")
    index_container: str = Field(default="", description="Индекс контейнера")
    number_container: str = Field(default="", description="Номер контейнера")
    release_order: str = Field(default="", description="Номер ордера")
    contract_terminal: str = Field(default="", description="Договор с терминалом")
    time_cancel: int = Field(default=30, description="Время отмены (минуты)")
    count_try: int = Field(default=60, description="Количество попыток")
    delay_try: int = Field(default=60, description="Задержка между попытками (секунды)")


class TaskResponse(BaseModel):
    """Модель ответа для задания"""
    id: str
    in_work: bool
    type_task: str
    status: str
    date: str
    time_slot: str
    time_cancel: int
    count_try: int
    delay_try: int
    num_auto: str
    driver: str
    place: str
    index_container: str
    number_container: str
    release_order: str
    contract_terminal: str
    created_at: str
    updated_at: str
    position: int


class TaskReorderRequest(BaseModel):
    """Модель для изменения порядка заданий"""
    task_positions: Dict[str, int] = Field(..., description="Словарь ID задания -> позиция")


# Модели для настроек
class SettingsResponse(BaseModel):
    """Модель ответа для настроек"""
    site_url: str
    login: str
    password: str
    refresh_interval: int
    connection_status: bool
    last_connection_test: Optional[str] = None
    default_execution_attempts: int
    default_delay_try: int
    element_timeout: int
    use_headless: bool
    save_credentials: bool
    browser_width: int
    browser_height: int
    browser_path: str
    slot_check_attempts: int
    slot_check_interval: int
    created_at: str
    updated_at: str


class SettingsUpdate(BaseModel):
    """Модель для обновления настроек"""
    site_url: str = Field(..., description="URL сайта")
    login: str = Field(..., description="Логин")
    password: str = Field(..., description="Пароль")
    refresh_interval: int = Field(default=30, description="Интервал обновления (секунды)")
    default_execution_attempts: int = Field(default=60, description="Количество попыток по умолчанию")
    default_delay_try: int = Field(default=60, description="Задержка между попытками по умолчанию (секунды)")
    element_timeout: int = Field(default=10, description="Таймаут элементов (секунды)")
    use_headless: bool = Field(default=False, description="Использовать headless режим")
    save_credentials: bool = Field(default=False, description="Сохранять учетные данные")
    browser_width: int = Field(default=1280, description="Ширина браузера")
    browser_height: int = Field(default=720, description="Высота браузера")
    browser_path: str = Field(default="", description="Путь к браузеру")
    slot_check_attempts: int = Field(default=10, description="Попытки проверки слота")
    slot_check_interval: int = Field(default=5, description="Интервал проверки слота (секунды)")


# Модели для справочников
class ReferenceItemResponse(BaseModel):
    """Модель ответа для элемента справочника"""
    id: str
    value: str
    description: str
    is_active: bool
    created_at: str
    updated_at: str


class ReferencesResponse(BaseModel):
    """Модель ответа для справочников"""
    operation_types: List[ReferenceItemResponse]
    statuses: List[ReferenceItemResponse]
    car_numbers: List[ReferenceItemResponse]
    drivers: List[ReferenceItemResponse]
    terminal_contracts: List[ReferenceItemResponse]
    time_slots: List[ReferenceItemResponse]
    updated_at: str


class ReferenceAddRequest(BaseModel):
    """Модель для добавления элемента справочника"""
    type: str = Field(..., description="Тип справочника")
    value: str = Field(..., description="Значение")
    description: str = Field(default="", description="Описание")


class ReferenceDeleteRequest(BaseModel):
    """Модель для удаления элемента справочника"""
    type: str = Field(..., description="Тип справочника")
    itemId: str = Field(..., description="ID элемента")


# Модели для логов
class LogEntryResponse(BaseModel):
    """Модель ответа для записи лога"""
    id: str
    timestamp: str
    level: str
    category: str
    message: str
    details: str
    task_id: str
    user_action: bool
    error: str


# Модели для автоматизации
class AutomationStartRequest(BaseModel):
    """Модель для запуска автоматизации"""
    taskIds: List[str] = Field(default_factory=list, description="Список ID заданий")
    taskId: Optional[str] = Field(default=None, description="ID одного задания (для обратной совместимости)")
    parallel: bool = Field(default=False, description="Параллельное выполнение")
    maxConcurrency: int = Field(default=5, description="Максимальная параллельность")


class AutomationResponse(BaseModel):
    """Модель ответа для автоматизации"""
    success: bool
    message: Optional[str] = None


# Модели для подключения
class ConnectionTestRequest(BaseModel):
    """Модель для тестирования подключения"""
    site_url: str = Field(..., description="URL сайта")
    login: str = Field(..., description="Логин")
    password: str = Field(..., description="Пароль")
    refresh_interval: Optional[int] = None
    default_execution_attempts: Optional[int] = None
    default_delay_try: Optional[int] = None
    element_timeout: Optional[int] = None
    use_headless: Optional[bool] = None
    save_credentials: Optional[bool] = None
    browser_width: Optional[int] = None
    browser_height: Optional[int] = None
    browser_path: Optional[str] = None
    slot_check_attempts: Optional[int] = None
    slot_check_interval: Optional[int] = None


class ConnectionTestResponse(BaseModel):
    """Модель ответа для тестирования подключения"""
    success: bool
    message: str
    error: str = ""
    duration: int = 0
    tested_at: str


# Общие модели ответов
class SuccessResponse(BaseModel):
    """Модель успешного ответа"""
    success: bool = True
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Модель ошибки"""
    error: str

