"""Flask веб-сервер"""
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import threading
from typing import Dict

from service.task_service import TaskService
from service.automation_service import AutomationService
from repository.json_repository import JSONDataManager
from domain.task import Task
from domain.settings import Settings
from domain.log import LogEntry, create_user_action_log
from domain.references import ReferenceType


class WebServer:
    """Flask веб-сервер"""
    
    def __init__(
        self,
        task_service: TaskService,
        automation_service: AutomationService,
        data_manager: JSONDataManager
    ):
        self.task_service = task_service
        self.automation_service = automation_service
        self.data_manager = data_manager
        
        # Создаем Flask приложение
        self.app = Flask(__name__, 
                         template_folder='templates',
                         static_folder='static')
        CORS(self.app)
        
        # Регистрируем маршруты
        self._register_routes()
    
    def _register_routes(self):
        """Регистрирует маршруты"""
        # Главная страница
        self.app.route('/')(self.index)
        
        # API заданий
        self.app.route('/api/tasks', methods=['GET'])(self.get_tasks)
        self.app.route('/api/tasks/create', methods=['POST'])(self.create_task)
        self.app.route('/api/tasks/update', methods=['PUT'])(self.update_task)
        self.app.route('/api/tasks/delete', methods=['DELETE'])(self.delete_task)
        self.app.route('/api/tasks/reorder', methods=['POST'])(self.reorder_tasks)
        
        # API настроек
        self.app.route('/api/settings', methods=['GET', 'POST'])(self.handle_settings)
        
        # API справочников
        self.app.route('/api/references', methods=['GET'])(self.get_references)
        self.app.route('/api/references/add', methods=['POST'])(self.add_reference)
        self.app.route('/api/references/delete', methods=['DELETE'])(self.delete_reference)
        
        # API логов
        self.app.route('/api/logs', methods=['GET'])(self.get_logs)
        
        # API автоматизации
        self.app.route('/api/automation/start', methods=['POST'])(self.start_automation)
        self.app.route('/api/automation/stop', methods=['POST'])(self.stop_automation)
        
        # API подключения
        self.app.route('/api/connection/test', methods=['POST'])(self.test_connection)
    
    def start(self, port: int = 8088):
        """Запускает сервер"""
        print(f"🚀 Веб-сервер запускается на порту {port}")
        print(f"🌐 Откройте в браузере: http://localhost:{port}")
        print("Нажмите Ctrl+C для остановки")
        
        self.app.run(host='0.0.0.0', port=port, debug=False)
    
    # =================== Маршруты ===================
    
    def index(self):
        """Главная страница"""
        return render_template('index.html')
    
    def get_tasks(self):
        """Получает список заданий"""
        try:
            tasks = self.task_service.get_all_tasks()
            return jsonify([task.to_dict() for task in tasks])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def create_task(self):
        """Создает новое задание"""
        try:
            data = request.get_json()
            
            # Создаем задание из данных
            task = Task(
                type_task=data.get('type_task', ''),
                status=data.get('status', 'Новый'),
                date=data.get('date', ''),
                time_slot=data.get('time_slot', ''),
                num_auto=data.get('num_auto', ''),
                driver=data.get('driver', ''),
                place=data.get('place', ''),
                index_container=data.get('index_container', ''),
                number_container=data.get('number_container', ''),
                release_order=data.get('release_order', ''),
                contract_terminal=data.get('contract_terminal', '')
            )
            
            self.task_service.create_task(task)
            return jsonify({'id': task.id, 'success': True})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def update_task(self):
        """Обновляет задание"""
        try:
            data = request.get_json()
            task = self.task_service.get_task(data['id'])
            
            # Обновляем поля
            task.in_work = data.get('in_work', False)
            task.type_task = data.get('type_task', '')
            task.status = data.get('status', '')
            task.date = data.get('date', '')
            task.time_slot = data.get('time_slot', '')
            task.time_cancel = data.get('time_cancel', 30)
            task.count_try = data.get('count_try', 60)
            task.num_auto = data.get('num_auto', '')
            task.driver = data.get('driver', '')
            task.place = data.get('place', '')
            task.index_container = data.get('index_container', '')
            task.number_container = data.get('number_container', '')
            task.release_order = data.get('release_order', '')
            task.contract_terminal = data.get('contract_terminal', '')
            
            self.task_service.update_task(task)
            return jsonify({'success': True})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def delete_task(self):
        """Удаляет задание"""
        try:
            task_id = request.args.get('id')
            if not task_id:
                return jsonify({'error': 'ID задания не указан'}), 400
            
            self.task_service.delete_task(task_id)
            return jsonify({'success': True})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def reorder_tasks(self):
        """Изменяет порядок заданий"""
        try:
            data = request.get_json()
            task_positions = data.get('task_positions', {})
            
            if not task_positions:
                return jsonify({'error': 'Позиции заданий не указаны'}), 400
            
            self.task_service.reorder_tasks(task_positions)
            return jsonify({'success': True})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def handle_settings(self):
        """Обрабатывает запросы настроек"""
        if request.method == 'GET':
            try:
                settings = self.data_manager.get_settings().get()
                return jsonify(settings.to_dict())
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        elif request.method == 'POST':
            try:
                data = request.get_json()
                settings = self.data_manager.get_settings().get()
                
                # Обновляем настройки
                new_settings = Settings.from_dict(data)
                settings.update(new_settings)
                
                self.data_manager.get_settings().update(settings)
                return jsonify({'success': True})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 400
    
    def get_references(self):
        """Получает справочники"""
        try:
            references = self.data_manager.get_references().get()
            return jsonify(references.to_dict())
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def add_reference(self):
        """Добавляет элемент в справочник"""
        try:
            data = request.get_json()
            ref_type_str = data.get('type', '')
            value = data.get('value', '')
            description = data.get('description', '')
            
            if not ref_type_str or not value:
                return jsonify({'error': 'Поля type и value обязательны'}), 400
            
            # Маппинг типов
            type_mapping = {
                'operations': ReferenceType.OPERATION,
                'statuses': ReferenceType.STATUS,
                'timeslots': ReferenceType.TIME_SLOT,
                'autos': ReferenceType.CAR_NUMBER,
                'drivers': ReferenceType.DRIVER,
                'contracts': ReferenceType.CONTRACT
            }
            
            ref_type = type_mapping.get(ref_type_str)
            if not ref_type:
                return jsonify({'error': 'Неизвестный тип справочника'}), 400
            
            # Валидация
            references = self.data_manager.get_references().get()
            is_valid, error_msg = references.validate_new_item(ref_type, value, description)
            
            if not is_valid:
                # Логируем попытку добавления дубликата
                log_entry = create_user_action_log(
                    "Попытка добавить дублирующуюся запись в справочник",
                    f"Тип: {ref_type_str}, Значение: {value}, Ошибка: {error_msg}"
                )
                self.data_manager.get_logs().save(log_entry)
                return jsonify({'error': error_msg}), 409 if 'существует' in error_msg else 400
            
            # Добавляем
            item = self.data_manager.get_references().add_item(ref_type, value, description)
            
            # Логируем
            log_entry = create_user_action_log(
                "Добавлена запись в справочник",
                f"Тип: {ref_type_str}, Значение: {value}"
            )
            self.data_manager.get_logs().save(log_entry)
            
            return jsonify({'success': True, 'item': item.to_dict()})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def delete_reference(self):
        """Удаляет элемент из справочника"""
        try:
            data = request.get_json()
            ref_type_str = data.get('type', '')
            item_id = data.get('itemId', '')
            
            if not ref_type_str or not item_id:
                return jsonify({'error': 'Поля type и itemId обязательны'}), 400
            
            # Маппинг типов
            type_mapping = {
                'operations': ReferenceType.OPERATION,
                'statuses': ReferenceType.STATUS,
                'timeslots': ReferenceType.TIME_SLOT,
                'autos': ReferenceType.CAR_NUMBER,
                'drivers': ReferenceType.DRIVER,
                'contracts': ReferenceType.CONTRACT
            }
            
            ref_type = type_mapping.get(ref_type_str)
            if not ref_type:
                return jsonify({'error': 'Неизвестный тип справочника'}), 400
            
            # Удаляем
            self.data_manager.get_references().remove_item(ref_type, item_id)
            
            # Логируем
            log_entry = create_user_action_log(
                "Удалена запись из справочника",
                f"Тип: {ref_type_str}, ID: {item_id}"
            )
            self.data_manager.get_logs().save(log_entry)
            
            return jsonify({'success': True})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def get_logs(self):
        """Получает логи"""
        try:
            logs = self.data_manager.get_logs().get_latest(100)
            return jsonify([log.to_dict() for log in logs])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def start_automation(self):
        """Запускает автоматизацию"""
        try:
            data = request.get_json()
            task_ids = data.get('taskIds', [])
            parallel = data.get('parallel', False)
            max_concurrency = data.get('maxConcurrency', 5)
            
            # Поддержка одиночного задания
            if 'taskId' in data:
                task_ids = [data['taskId']]
            
            if not task_ids:
                return jsonify({'error': 'Не указаны задания для выполнения'}), 400
            
            # Определяем режим
            execution_mode = "параллельная" if parallel else "последовательная"
            
            # Логируем запуск
            start_log = LogEntry(
                level='INFO',
                category='BROWSER_AUTOMATION',
                message=f"🚀 Запуск автоматизации для {len(task_ids)} заданий ({execution_mode} обработка)"
            )
            self.data_manager.get_logs().save(start_log)
            
            # Запускаем в отдельном потоке
            def run_automation():
                try:
                    if parallel:
                        self.automation_service.execute_tasks_parallel(task_ids, max_concurrency)
                    else:
                        self.automation_service.execute_tasks_sequentially(task_ids)
                    
                    # Логируем успех
                    success_log = LogEntry(
                        level='INFO',
                        category='BROWSER_AUTOMATION',
                        message=f"✅ Автоматизация всех заданий успешно завершена ({len(task_ids)} заданий, {execution_mode})"
                    )
                    self.data_manager.get_logs().save(success_log)
                    
                except Exception as e:
                    # Логируем ошибку
                    error_log = LogEntry(
                        level='ERROR',
                        category='BROWSER_AUTOMATION',
                        message=f"❌ Ошибка автоматизации: {str(e)}"
                    )
                    self.data_manager.get_logs().save(error_log)
            
            thread = threading.Thread(target=run_automation, daemon=True)
            thread.start()
            
            return jsonify({'success': True})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def stop_automation(self):
        """Останавливает автоматизацию"""
        try:
            self.automation_service.stop_execution()
            self.task_service.stop_task_execution()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def test_connection(self):
        """Тестирует подключение"""
        try:
            data = request.get_json()
            
            # Валидация
            if not data.get('site_url'):
                return jsonify({'error': 'URL сайта не указан'}), 400
            if not data.get('login'):
                return jsonify({'error': 'Логин не указан'}), 400
            if not data.get('password'):
                return jsonify({'error': 'Пароль не указан'}), 400
            
            # Создаем настройки из данных
            settings = Settings.from_dict(data)
            
            # Сохраняем настройки
            current_settings = self.data_manager.get_settings().get()
            current_settings.update(settings)
            self.data_manager.get_settings().update(current_settings)
            
            # Выполняем тест подключения
            result = self.automation_service.test_connection()
            
            return jsonify(result.to_dict())
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400


def create_web_server(
    task_service: TaskService,
    automation_service: AutomationService,
    data_manager: JSONDataManager
) -> WebServer:
    """Создает веб-сервер"""
    return WebServer(task_service, automation_service, data_manager)

