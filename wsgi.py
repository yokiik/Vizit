"""
WSGI точка входа для Gunicorn
"""

import sys
from pathlib import Path

# Добавляем текущую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from main import create_web_server
from repository.json_repository import JSONDataManager
from service.task_service import TaskService
from service.automation_service import AutomationService
from domain.log import LogEntry, LogLevel, LogCategory

def create_app():
    """Создает WSGI приложение для Gunicorn"""
    
    print("🔧 Инициализация RLI Systems...")
    
    # Определяем директорию данных
    home_dir = Path.home()
    data_dir = home_dir / ".rlisystems_python"
    
    # Инициализируем менеджер данных
    data_manager = JSONDataManager(str(data_dir))
    data_manager.initialize()
    
    if not data_manager.is_healthy():
        raise RuntimeError("Хранилище данных находится в неисправном состоянии")
    
    print("✓ Хранилище данных инициализировано")
    
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
    
    print("✓ Бизнес-сервисы созданы")
    
    # Создаем веб-сервер
    web_server = create_web_server(task_service, automation_service, data_manager)
    
    # Логируем запуск
    startup_log = LogEntry(
        level=LogLevel.INFO,
        category=LogCategory.SYSTEM,
        message="Веб-приложение запущено через Gunicorn"
    )
    data_manager.get_logs().save(startup_log)
    
    print("✓ Веб-сервер готов")
    
    return web_server.app

# Gunicorn ожидает переменную 'application'
application = create_app()

# Для запуска в режиме разработки
if __name__ == "__main__":
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('0.0.0.0', 8088, app, use_reloader=True)

