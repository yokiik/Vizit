"""Точка входа приложения RLI Systems v2 Python"""
import os
import signal
import sys
from pathlib import Path

from repository.json_repository import JSONDataManager
from service.task_service import TaskService
from service.automation_service import AutomationService
from web.server import create_web_server
from domain.log import LogEntry, LogLevel, LogCategory


def main():
    """Главная функция"""
    print("=== RLI Systems Python Version ===")
    print("Starting web interface...")
    
    # Определяем директорию данных
    home_dir = Path.home()
    data_dir = home_dir / ".rlisystems_python"
    
    # Инициализируем менеджер данных
    data_manager = JSONDataManager(str(data_dir))
    
    try:
        data_manager.initialize()
    except Exception as e:
        print(f"Ошибка инициализации хранилища данных: {e}")
        sys.exit(1)
    
    # Проверяем здоровье хранилища
    if not data_manager.is_healthy():
        print("Хранилище данных находится в неисправном состоянии")
        sys.exit(1)
    
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
    
    # Обработчик сигналов для graceful shutdown
    def signal_handler(signum, frame):
        print("\nПолучен сигнал завершения. Закрытие приложения...")
        
        # Логируем завершение
        shutdown_log = LogEntry(
            level=LogLevel.INFO,
            category=LogCategory.SYSTEM,
            message="Веб-приложение завершает работу"
        )
        data_manager.get_logs().save(shutdown_log)
        
        data_manager.close()
        print("Приложение успешно завершено")
        sys.exit(0)
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Получаем порт из переменной окружения или используем по умолчанию
    port = int(os.getenv('PORT', 8088))
    
    # Логируем запуск
    startup_log = LogEntry(
        level=LogLevel.INFO,
        category=LogCategory.SYSTEM,
        message=f"Веб-приложение запущено на порту {port}"
    )
    data_manager.get_logs().save(startup_log)
    
    # Запускаем веб-сервер через Uvicorn
    try:
        import uvicorn
        print(f"[INFO] Starting server on port {port}")
        print(f"[INFO] Open browser: http://localhost:{port}")
        print(f"[INFO] Swagger docs: http://localhost:{port}/docs")
        print("Press Ctrl+C to stop")
        uvicorn.run(web_server.app, host="0.0.0.0", port=port, log_level="info")
    except Exception as e:
        print(f"[ERROR] Server startup error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

