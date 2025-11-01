"""FastAPI веб-сервер"""
from fastapi import FastAPI, HTTPException, Query, Request, Body
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
import threading
from typing import List

from service.task_service import TaskService
from service.automation_service import AutomationService
from repository.json_repository import JSONDataManager
from domain.task import Task
from domain.settings import Settings
from domain.log import LogEntry, LogLevel, LogCategory, create_user_action_log
from domain.references import ReferenceType
from .schemas import (
    TaskCreate, TaskUpdate, TaskResponse, TaskReorderRequest,
    SettingsResponse, SettingsUpdate,
    ReferencesResponse, ReferenceAddRequest, ReferenceDeleteRequest, ReferenceItemResponse,
    LogEntryResponse,
    AutomationStartRequest, AutomationResponse,
    ConnectionTestRequest, ConnectionTestResponse,
    SuccessResponse, ErrorResponse,
    LoginRequest, LoginResponse
)


class WebServer:
    """FastAPI веб-сервер"""
    
    def __init__(
        self,
        task_service: TaskService,
        automation_service: AutomationService,
        data_manager: JSONDataManager
    ):
        self.task_service = task_service
        self.automation_service = automation_service
        self.data_manager = data_manager
        
        # Создаем FastAPI приложение
        self.app = FastAPI(
            title="RLI Systems API",
            description="API для автоматизации регистрации ввозы/вывоза контейнеров",
            version="2.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Статические файлы и шаблоны
        from pathlib import Path
        import os
        
        # Определяем базовую директорию
        base_dir = Path(__file__).parent.parent
        static_dir = base_dir / "web" / "static"
        templates_dir = base_dir / "web" / "templates"
        
        if static_dir.exists():
            self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        # Инициализируем Jinja2 окружение
        if templates_dir.exists():
            self.templates_env = Environment(loader=FileSystemLoader(str(templates_dir)))
        else:
            self.templates_env = None
        
        # Регистрируем маршруты
        self._register_routes()
    
    def _register_routes(self):
        """Регистрирует маршруты"""
        
        # Главная страница
        @self.app.get("/", response_class=HTMLResponse)
        async def index(request: Request):
            """Главная страница"""
            if self.templates_env:
                template = self.templates_env.get_template("index.html")
                return HTMLResponse(content=template.render())
            else:
                return HTMLResponse(content="<h1>RLI Systems</h1><p>Template not found</p>")
        
        # API авторизации
        @self.app.post("/auth/login", response_model=LoginResponse)
        async def auth_login(request: LoginRequest, response: Response):
            """Авторизация пользователя"""
            try:
                # Получаем логин (поддержка username или login)
                username = request.username or request.login
                password = request.password
                
                if not username or not password:
                    response.status_code = 400
                    return LoginResponse(
                        success=False,
                        message="Username and password required"
                    )
                
                # Проверяем: логин и пароль должны быть "admin"
                if username == "admin" and password == "admin":
                    # Логируем успешную авторизацию
                    log_entry = create_user_action_log(
                        "Успешная авторизация",
                        f"Пользователь: {username}"
                    )
                    self.data_manager.get_logs().save(log_entry)
                    
                    response.status_code = 200
                    return LoginResponse(
                        success=True,
                        message="Login successful",
                        token="bearer-token-placeholder",
                        user={
                            "username": username,
                            "role": "admin"
                        }
                    )
                else:
                    # Логируем неудачную попытку
                    log_entry = create_user_action_log(
                        "Неудачная попытка авторизации",
                        f"Пользователь: {username}"
                    )
                    self.data_manager.get_logs().save(log_entry)
                    
                    response.status_code = 401
                    return LoginResponse(
                        success=False,
                        message="Invalid credentials"
                    )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # API заданий
        @self.app.get("/api/tasks", response_model=List[TaskResponse])
        async def get_tasks():
            """Получает список заданий"""
            try:
                tasks = self.task_service.get_all_tasks()
                return [TaskResponse(**task.to_dict()) for task in tasks]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/tasks/create", response_model=SuccessResponse)
        async def create_task(task_data: TaskCreate):
            """Создает новое задание"""
            try:
                task = Task(
                    type_task=task_data.type_task,
                    status=task_data.status,
                    date=task_data.date,
                    time_slot=task_data.time_slot,
                    num_auto=task_data.num_auto,
                    driver=task_data.driver,
                    place=task_data.place,
                    index_container=task_data.index_container,
                    number_container=task_data.number_container,
                    release_order=task_data.release_order,
                    contract_terminal=task_data.contract_terminal,
                    time_cancel=task_data.time_cancel,
                    count_try=task_data.count_try,
                    delay_try=task_data.delay_try
                )
                
                self.task_service.create_task(task)
                return SuccessResponse(message=f"Задание создано с ID: {task.id}")
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.put("/api/tasks/update", response_model=SuccessResponse)
        async def update_task(task_data: TaskUpdate):
            """Обновляет задание"""
            try:
                task = self.task_service.get_task(task_data.id)
                
                # Обновляем поля
                task.in_work = task_data.in_work
                task.type_task = task_data.type_task
                task.status = task_data.status
                task.date = task_data.date
                task.time_slot = task_data.time_slot
                task.time_cancel = task_data.time_cancel
                task.count_try = task_data.count_try
                task.delay_try = task_data.delay_try
                task.num_auto = task_data.num_auto
                task.driver = task_data.driver
                task.place = task_data.place
                task.index_container = task_data.index_container
                task.number_container = task_data.number_container
                task.release_order = task_data.release_order
                task.contract_terminal = task_data.contract_terminal
                
                self.task_service.update_task(task)
                return SuccessResponse()
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.delete("/api/tasks/delete", response_model=SuccessResponse)
        async def delete_task(task_id: str = Query(..., description="ID задания")):
            """Удаляет задание"""
            try:
                if not task_id:
                    raise HTTPException(status_code=400, detail="ID задания не указан")
                
                self.task_service.delete_task(task_id)
                return SuccessResponse()
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/api/tasks/reorder", response_model=SuccessResponse)
        async def reorder_tasks(request_data: TaskReorderRequest):
            """Изменяет порядок заданий"""
            try:
                if not request_data.task_positions:
                    raise HTTPException(status_code=400, detail="Позиции заданий не указаны")
                
                self.task_service.reorder_tasks(request_data.task_positions)
                return SuccessResponse()
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # API настроек
        @self.app.get("/api/settings", response_model=SettingsResponse)
        async def get_settings():
            """Получает настройки"""
            try:
                settings = self.data_manager.get_settings().get()
                return SettingsResponse(**settings.to_dict())
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/settings", response_model=SuccessResponse)
        async def update_settings(settings_data: SettingsUpdate):
            """Обновляет настройки"""
            try:
                settings = self.data_manager.get_settings().get()
                
                # Обновляем настройки
                new_settings = Settings.from_dict(settings_data.model_dump())
                settings.update(new_settings)
                
                self.data_manager.get_settings().update(settings)
                return SuccessResponse()
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # API справочников
        @self.app.get("/api/references", response_model=ReferencesResponse)
        async def get_references():
            """Получает справочники"""
            try:
                references = self.data_manager.get_references().get()
                ref_dict = references.to_dict()
                # Преобразуем в нужный формат
                return ReferencesResponse(
                    operation_types=[ReferenceItemResponse(**item) for item in ref_dict["operation_types"]],
                    statuses=[ReferenceItemResponse(**item) for item in ref_dict["statuses"]],
                    car_numbers=[ReferenceItemResponse(**item) for item in ref_dict["car_numbers"]],
                    drivers=[ReferenceItemResponse(**item) for item in ref_dict["drivers"]],
                    terminal_contracts=[ReferenceItemResponse(**item) for item in ref_dict["terminal_contracts"]],
                    time_slots=[ReferenceItemResponse(**item) for item in ref_dict["time_slots"]],
                    updated_at=ref_dict["updated_at"]
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/references/add", response_model=SuccessResponse)
        async def add_reference(request_data: ReferenceAddRequest):
            """Добавляет элемент в справочник"""
            try:
                if not request_data.type or not request_data.value:
                    raise HTTPException(status_code=400, detail="Поля type и value обязательны")
                
                # Маппинг типов
                type_mapping = {
                    'operations': ReferenceType.OPERATION,
                    'statuses': ReferenceType.STATUS,
                    'timeslots': ReferenceType.TIME_SLOT,
                    'autos': ReferenceType.CAR_NUMBER,
                    'drivers': ReferenceType.DRIVER,
                    'contracts': ReferenceType.CONTRACT
                }
                
                ref_type = type_mapping.get(request_data.type)
                if not ref_type:
                    raise HTTPException(status_code=400, detail="Неизвестный тип справочника")
                
                # Валидация
                references = self.data_manager.get_references().get()
                is_valid, error_msg = references.validate_new_item(
                    ref_type, request_data.value, request_data.description
                )
                
                if not is_valid:
                    # Логируем попытку добавления дубликата
                    log_entry = create_user_action_log(
                        "Попытка добавить дублирующуюся запись в справочник",
                        f"Тип: {request_data.type}, Значение: {request_data.value}, Ошибка: {error_msg}"
                    )
                    self.data_manager.get_logs().save(log_entry)
                    status_code = 409 if 'существует' in error_msg else 400
                    raise HTTPException(status_code=status_code, detail=error_msg)
                
                # Добавляем
                item = self.data_manager.get_references().add_item(
                    ref_type, request_data.value, request_data.description
                )
                
                # Логируем
                log_entry = create_user_action_log(
                    "Добавлена запись в справочник",
                    f"Тип: {request_data.type}, Значение: {request_data.value}"
                )
                self.data_manager.get_logs().save(log_entry)
                
                return SuccessResponse(message=f"Элемент добавлен: {item.id}")
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.delete("/api/references/delete", response_model=SuccessResponse)
        async def delete_reference(request_data: ReferenceDeleteRequest = Body(...)):
            """Удаляет элемент из справочника"""
            try:
                if not request_data.type or not request_data.itemId:
                    raise HTTPException(status_code=400, detail="Поля type и itemId обязательны")
                
                # Маппинг типов
                type_mapping = {
                    'operations': ReferenceType.OPERATION,
                    'statuses': ReferenceType.STATUS,
                    'timeslots': ReferenceType.TIME_SLOT,
                    'autos': ReferenceType.CAR_NUMBER,
                    'drivers': ReferenceType.DRIVER,
                    'contracts': ReferenceType.CONTRACT
                }
                
                ref_type = type_mapping.get(request_data.type)
                if not ref_type:
                    raise HTTPException(status_code=400, detail="Неизвестный тип справочника")
                
                # Удаляем
                self.data_manager.get_references().remove_item(ref_type, request_data.itemId)
                
                # Логируем
                log_entry = create_user_action_log(
                    "Удалена запись из справочника",
                    f"Тип: {request_data.type}, ID: {request_data.itemId}"
                )
                self.data_manager.get_logs().save(log_entry)
                
                return SuccessResponse()
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # API логов
        @self.app.get("/api/logs", response_model=List[LogEntryResponse])
        async def get_logs():
            """Получает логи"""
            try:
                logs = self.data_manager.get_logs().get_latest(100)
                return [LogEntryResponse(**log.to_dict()) for log in logs]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # API автоматизации
        @self.app.post("/api/automation/start", response_model=AutomationResponse)
        async def start_automation(request_data: AutomationStartRequest):
            """Запускает автоматизацию"""
            try:
                task_ids = request_data.taskIds
                
                # Поддержка одиночного задания
                if request_data.taskId:
                    task_ids = [request_data.taskId]
                
                if not task_ids:
                    raise HTTPException(status_code=400, detail="Не указаны задания для выполнения")
                
                # Определяем режим
                execution_mode = "параллельная" if request_data.parallel else "последовательная"
                
                # Логируем запуск
                start_log = LogEntry(
                    level=LogLevel.INFO,
                    category=LogCategory.BROWSER_AUTOMATION,
                    message=f"🚀 Запуск автоматизации для {len(task_ids)} заданий ({execution_mode} обработка)"
                )
                self.data_manager.get_logs().save(start_log)
                
                # Запускаем в отдельном потоке
                def run_automation():
                    try:
                        if request_data.parallel:
                            self.automation_service.execute_tasks_parallel(
                                task_ids, request_data.maxConcurrency
                            )
                        else:
                            self.automation_service.execute_tasks_sequentially(task_ids)
                        
                        # Логируем успех
                        success_log = LogEntry(
                            level=LogLevel.INFO,
                            category=LogCategory.BROWSER_AUTOMATION,
                            message=f"✅ Автоматизация всех заданий успешно завершена ({len(task_ids)} заданий, {execution_mode})"
                        )
                        self.data_manager.get_logs().save(success_log)
                    except Exception as e:
                        # Логируем ошибку
                        error_log = LogEntry(
                            level=LogLevel.ERROR,
                            category=LogCategory.BROWSER_AUTOMATION,
                            message=f"❌ Ошибка автоматизации: {str(e)}"
                        )
                        self.data_manager.get_logs().save(error_log)
                
                thread = threading.Thread(target=run_automation, daemon=True)
                thread.start()
                
                return AutomationResponse(success=True)
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/api/automation/stop", response_model=AutomationResponse)
        async def stop_automation():
            """Останавливает автоматизацию"""
            try:
                self.automation_service.stop_execution()
                self.task_service.stop_task_execution()
                return AutomationResponse(success=True)
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # API подключения
        @self.app.post("/api/connection/test", response_model=ConnectionTestResponse)
        async def test_connection(request_data: ConnectionTestRequest):
            """Тестирует подключение"""
            try:
                # Валидация
                if not request_data.site_url:
                    raise HTTPException(status_code=400, detail="URL сайта не указан")
                if not request_data.login:
                    raise HTTPException(status_code=400, detail="Логин не указан")
                if not request_data.password:
                    raise HTTPException(status_code=400, detail="Пароль не указан")
                
                # Создаем настройки из данных
                settings_dict = request_data.model_dump(exclude_none=True)
                settings = Settings.from_dict(settings_dict)
                
                # Сохраняем настройки
                current_settings = self.data_manager.get_settings().get()
                current_settings.update(settings)
                self.data_manager.get_settings().update(current_settings)
                
                # Выполняем тест подключения
                result = self.automation_service.test_connection()
                
                return ConnectionTestResponse(**result.to_dict())
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))


def create_web_server(
    task_service: TaskService,
    automation_service: AutomationService,
    data_manager: JSONDataManager
) -> WebServer:
    """Создает веб-сервер"""
    return WebServer(task_service, automation_service, data_manager)
