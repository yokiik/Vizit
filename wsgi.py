"""
ASGI точка входа для Uvicorn
"""

import sys
import os
from pathlib import Path

# Добавляем текущую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from web.server import create_web_server
from repository.json_repository import JSONDataManager
from service.task_service import TaskService
from service.automation_service import AutomationService
from domain.log import LogEntry, LogLevel, LogCategory

def create_app():
    """Создает FastAPI приложение для Uvicorn"""
    
    print("[INFO] Initializing RLI Systems...")
    
    # Определяем директорию данных
    home_dir = Path.home()
    data_dir = home_dir / ".rlisystems_python"
    
    # Инициализируем менеджер данных
    data_manager = JSONDataManager(str(data_dir))
    data_manager.initialize()
    
    if not data_manager.is_healthy():
        raise RuntimeError("Data storage is unhealthy")
    
    print("[OK] Data storage initialized")
    
    # Создаем сервисы
    task_service = TaskService(
        data_manager.get_tasks(),
        data_manager.get_logs(),
        data_manager.get_references(),
        data_manager.get_settings()
    )
    
    automation_service = AutomationService(
        data_manager.get_settings(),
        data_manager.get_logs(),
        task_service
    )
    
    print("[OK] Business services created")
    
    # Создаем веб-сервер
    web_server = create_web_server(task_service, automation_service, data_manager)
    
    # Логируем запуск
    startup_log = LogEntry(
        level=LogLevel.INFO,
        category=LogCategory.SYSTEM,
        message="Web application started via Uvicorn"
    )
    data_manager.get_logs().save(startup_log)
    
    print("[OK] Web server ready")
    
    return web_server.app

# Uvicorn ожидает переменную 'application'
application = create_app()

# Для запуска в режиме разработки
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8088))
    uvicorn.run("wsgi:application", host="0.0.0.0", port=port, reload=False)

