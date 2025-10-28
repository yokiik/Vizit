"""Конфигурация Gunicorn для production развертывания"""

import multiprocessing
import os

# Количество worker процессов
# Рекомендация: (2 × количество ядер CPU) + 1
workers = multiprocessing.cpu_count() * 2 + 1
if workers > 8:
    workers = 8  # Ограничиваем максимум 8 workers

# Тип worker
worker_class = 'sync'

# Количество worker потоков (для многопоточных приложений)
threads = 2

# Биндинг
bind = f"0.0.0.0:{os.getenv('PORT', '8088')}"

# Таймауты
timeout = 300  # 5 минут для браузерной автоматизации
graceful_timeout = 30
keepalive = 5

# Логирование
loglevel = 'info'
accesslog = '-'
errorlog = '-'

# Имя процесса
proc_name = 'rli-systems'

# Максимальное количество одновременных запросов
max_requests = 1000
max_requests_jitter = 50

# Перезагрузка при изменении кода (только для разработки)
reload = False

# PID файл
pidfile = None  # Можно указать путь: '/var/run/rli-systems.pid'

# User и Group (настройте при необходимости)
# user = 'www-data'
# group = 'www-data'

# Preload приложения для экономии памяти
preload_app = False  # Установите True если нет проблем с многопроцессностью

# Метод сохранения
worker_tmp_dir = '/dev/shm'  # Использует shared memory для временных файлов

def on_starting(server):
    """Вызывается при запуске главного процесса"""
    print("🚀 RLI Systems server starting...")

def on_reload(server):
    """Вызывается при перезагрузке"""
    print("🔄 RLI Systems server reloading...")

def worker_exit(server, worker):
    """Вызывается при остановке worker"""
    print(f"👋 Worker {worker.pid} exiting...")

def on_exit(server):
    """Вызывается при завершении главного процесса"""
    print("🛑 RLI Systems server exiting...")

