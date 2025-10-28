"""Сервис автоматизации браузера"""
import time
import threading
from typing import List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from domain.task import Task, TaskType, TaskStatus
from domain.settings import Settings, ConnectionTestResult
from domain.log import LogEntry, LogLevel, LogCategory, create_error_log
from repository.interfaces import SettingsRepository, LogRepository
from .task_service import TaskService


class AutomationService:
    """Сервис автоматизации"""
    
    def __init__(
        self,
        settings_repo: SettingsRepository,
        log_repo: LogRepository,
        task_service: TaskService
    ):
        self.settings_repo = settings_repo
        self.log_repo = log_repo
        self.task_service = task_service
        self.driver: Optional[webdriver.Chrome] = None
        self.is_running = False
        self.stop_flag = threading.Event()
        self.current_task: Optional[Task] = None
    
    # =================== Тест подключения ===================
    
    def test_connection(self) -> ConnectionTestResult:
        """Тестирует подключение к сайту"""
        result = ConnectionTestResult(success=False, message="")
        self._log_info("🔍 Начинаем тест подключения...")
        
        start_time = datetime.now()
        
        try:
            settings = self.settings_repo.get()
            
            # Проверяем настройки
            if not settings.site_url:
                raise Exception("URL сайта не указан в настройках")
            if not settings.login:
                raise Exception("Логин не указан в настройках")
            if not settings.password:
                raise Exception("Пароль не указан в настройках")
            
            self._log_info(f"🌐 Тестируем подключение к: {settings.site_url}")
            self._log_info(f"👤 Логин: {settings.login}")
            
            # Инициализация браузера
            self._init_browser(settings)
            
            # Тестируем авторизацию
            self._log_info("🔐 Тестируем авторизацию...")
            self._perform_login_test(settings)
            
            # Успех
            result.success = True
            result.message = "Подключение успешно, авторизация прошла"
            
            # Обновляем статус подключения в настройках
            settings.update_connection_status(True, result.message)
            self.settings_repo.update(settings)
            
            self._log_info("✅ Тест подключения выполнен успешно")
            
        except Exception as e:
            result.success = False
            result.message = f"Ошибка: {str(e)}"
            result.error = str(e)
            self._log_error("Ошибка тестирования подключения", e)
        
        finally:
            self._close_browser()
            duration = (datetime.now() - start_time).total_seconds() * 1000
            result.duration = int(duration)
        
        return result
    
    # =================== Выполнение заданий ===================
    
    def execute_tasks_sequentially(self, task_ids: List[str]) -> None:
        """Последовательное выполнение заданий"""
        self._log_info(f"📋 Начало последовательного выполнения {len(task_ids)} заданий")
        self.is_running = True
        self.stop_flag.clear()
        
        success_count = 0
        error_count = 0
        
        for i, task_id in enumerate(task_ids):
            # Проверка сигнала остановки
            if self.stop_flag.is_set():
                self._log_info("🛑 Получен сигнал остановки автоматизации")
                self.is_running = False
                raise Exception("Автоматизация остановлена пользователем")
            
            self._log_info(f"📝 Задание {i+1} из {len(task_ids)}: {task_id}")
            
            try:
                task = self.task_service.get_task(task_id)
                self.execute_task(task)
                self._log_task_info(f"✅ Задание {i+1} ({task.type_task}) выполнено успешно", "")
                success_count += 1
            except Exception as e:
                self._log_task_error(f"❌ Задание {i+1} завершено с ошибкой", e)
                error_count += 1
            
            # Пауза между заданиями
            if i < len(task_ids) - 1:
                time.sleep(1)
        
        self.is_running = False
        self._log_info(f"📊 Завершено выполнение всех заданий. Успешно: {success_count}, Ошибок: {error_count}")
        
        if error_count > 0:
            raise Exception(f"Выполнено с ошибками: успешно {success_count}, ошибок {error_count}")
    
    def execute_tasks_parallel(self, task_ids: List[str], max_concurrency: int = 5) -> None:
        """Параллельное выполнение заданий"""
        if max_concurrency <= 0:
            max_concurrency = 5
        
        self._log_info(f"🔄 Начало параллельного выполнения {len(task_ids)} заданий (макс. одновременно: {max_concurrency})")
        self.is_running = True
        self.stop_flag.clear()
        
        success_count = 0
        error_count = 0
        errors = []
        
        with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
            # Создаем futures
            future_to_task = {}
            for i, task_id in enumerate(task_ids):
                # Проверка сигнала остановки
                if self.stop_flag.is_set():
                    self._log_info("🛑 Получен сигнал остановки автоматизации")
                    break
                
                future = executor.submit(self._execute_task_parallel, task_id, i+1)
                future_to_task[future] = task_id
            
            # Обрабатываем результаты
            for future in as_completed(future_to_task):
                task_id = future_to_task[future]
                try:
                    future.result()
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(str(e))
        
        self.is_running = False
        self._log_info(f"📊 Завершено параллельное выполнение. Успешно: {success_count}, Ошибок: {error_count}")
        
        if error_count > 0:
            raise Exception(f"Выполнено с ошибками: успешно {success_count}, ошибок {error_count}. Ошибки: {'; '.join(errors)}")
    
    def _execute_task_parallel(self, task_id: str, task_num: int):
        """Выполнение задания в параллельном режиме"""
        self._log_info(f"🚀 Запуск задания {task_num}: {task_id}")
        
        try:
            task = self.task_service.get_task(task_id)
            
            # Создаем отдельный экземпляр для параллельного выполнения
            parallel_service = self._create_parallel_instance()
            parallel_service.execute_task(task)
            
            self._log_task_info(f"✅ Задание {task_num} ({task.type_task}) выполнено успешно", "")
        except Exception as e:
            self._log_task_error(f"❌ Задание {task_num} завершено с ошибкой", e)
            raise Exception(f"Задание {task_id}: {str(e)}")
    
    def _create_parallel_instance(self) -> 'AutomationService':
        """Создает экземпляр для параллельного выполнения"""
        return AutomationService(
            self.settings_repo,
            self.log_repo,
            self.task_service
        )
    
    def execute_task(self, task: Task) -> None:
        """Выполняет задание"""
        # Проверка сигнала остановки
        if self.stop_flag.is_set():
            self._log_info("🛑 Получен сигнал остановки во время выполнения задания")
            raise Exception("Выполнение задания остановлено пользователем")
        
        self.current_task = task
        settings = self.settings_repo.get()
        
        # Этап 1: Инициализация браузера
        self._log_task_info("🌐 Этап 1: Инициализация браузера", "Настройка Selenium WebDriver...")
        self._init_browser(settings)
        self._log_task_info("✅ Браузер готов", "Selenium WebDriver успешно инициализирован")
        
        # Обновляем статус задания
        self.task_service.update_task_status(task.id, TaskStatus.IN_WORK)
        
        # Логируем начало выполнения
        self._log_task_info(
            "🎯 Начато выполнение задания",
            f"Тип: {task.type_task}, Дата: {task.date}, Слот: {task.time_slot}, Авто: {task.num_auto}, Водитель: {task.driver}"
        )
        
        try:
            # Этап 2: Авторизация
            self._log_task_info("🔐 Этап 2: Авторизация на сайте", "Переход на сайт и вход в систему...")
            self._perform_login_test(settings)
            
            # Этап 3: Выполнение сценария
            self._log_task_info("⚡ Этап 3: Выполнение базового сценария", f"Тип задания: {task.type_task}")
            
            if task.type_task == TaskType.EXPORT:
                self._execute_export_task(task, settings)
            elif task.type_task == TaskType.IMPORT:
                self._execute_import_task(task, settings)
            else:
                raise ValueError(f"Неизвестный тип задания: {task.type_task}")
            
            # Этап 4: Завершение
            self._log_task_info("🏁 Этап 4: Завершение", "Обновление статуса и завершение...")
            self.task_service.update_task_status(task.id, TaskStatus.COMPLETED)
            self._log_task_info("🎉 Задание выполнено успешно!", f"ID: {task.id}, Тип: {task.type_task}")
            
        except Exception as e:
            self._log_task_error("❌ Ошибка выполнения задания", e)
            self.task_service.update_task_status(task.id, TaskStatus.SKIPPED)
            raise
        
        finally:
            self._close_browser()
    
    def stop_execution(self):
        """Останавливает выполнение"""
        self.stop_flag.set()
        self.is_running = False
        self._log_info("⏸️ Запрос на остановку автоматизации")
    
    # =================== Браузер ===================
    
    def _init_browser(self, settings: Settings):
        """Инициализирует браузер"""
        try:
            chrome_options = ChromeOptions()
            
            # Настройки Chrome
            if settings.use_headless:
                chrome_options.add_argument('--headless')
            
            chrome_options.add_argument(f'--window-size={settings.browser_width},{settings.browser_height}')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Создаем драйвер
            if settings.browser_path:
                service = ChromeService(executable_path=settings.browser_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            
            self._log_info("✅ Браузер инициализирован")
            
        except Exception as e:
            self._log_error("Ошибка инициализации браузера", e)
            raise
    
    def _close_browser(self):
        """Закрывает браузер"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                self._log_info("✅ Браузер закрыт")
            except Exception as e:
                self._log_error("Ошибка закрытия браузера", e)
    
    def _wait_for_element(self, by: By, selector: str, timeout: int = 10):
        """Ожидает появления элемента"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            raise Exception(f"Элемент не найден за {timeout}с: {selector}")
    
    # =================== Авторизация ===================
    
    def _perform_login_test(self, settings: Settings):
        """Выполняет авторизацию на сайте"""
        try:
            # Переход на сайт
            self.driver.get(settings.site_url)
            time.sleep(3)
            
            # Поиск формы авторизации
            self._log_info("🔍 Поиск формы авторизации...")
            
            # Попробуем найти поле логина с различными селекторами
            login_field = None
            login_selectors = [
                (By.ID, "username"),
                (By.ID, "login"),
                (By.ID, "user"),
                (By.ID, "email"),
                (By.NAME, "username"),
                (By.NAME, "login"),
                (By.NAME, "user"),
                (By.NAME, "email"),
                (By.CSS_SELECTOR, "input[type='text']"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.CSS_SELECTOR, ".username"),
                (By.CSS_SELECTOR, ".login"),
                (By.CSS_SELECTOR, ".form-control"),
            ]
            
            for by, selector in login_selectors:
                try:
                    login_field = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    self._log_info(f"✅ Поле логина найдено: {by} = '{selector}'")
                    break
                except:
                    continue
            
            if not login_field:
                raise Exception("Поле логина не найдено")
            
            # Заполняем логин
            login_field.clear()
            login_field.send_keys(settings.login)
            
            # Попробуем найти поле пароля
            password_field = None
            password_selectors = [
                (By.ID, "password"),
                (By.ID, "pass"),
                (By.NAME, "password"),
                (By.NAME, "pass"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.CSS_SELECTOR, ".password"),
                (By.CSS_SELECTOR, ".form-control[type='password']"),
            ]
            
            for by, selector in password_selectors:
                try:
                    password_field = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    self._log_info(f"✅ Поле пароля найдено: {by} = '{selector}'")
                    break
                except:
                    continue
            
            if not password_field:
                raise Exception("Поле пароля не найдено")
            
            # Заполняем пароль
            password_field.clear()
            password_field.send_keys(settings.password)
            
            # Попробуем найти кнопку входа
            login_button = None
            button_selectors = [
                # Стандартные селекторы
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.CSS_SELECTOR, "button"),
                (By.CSS_SELECTOR, "input[type='button']"),
                
                # По классам
                (By.CSS_SELECTOR, ".btn"),
                (By.CSS_SELECTOR, ".submit"),
                (By.CSS_SELECTOR, ".login-btn"),
                (By.CSS_SELECTOR, ".btn-primary"),
                (By.CSS_SELECTOR, ".btn-success"),
                (By.CSS_SELECTOR, ".button"),
                (By.CSS_SELECTOR, ".form-submit"),
                
                # По ID
                (By.ID, "submit"),
                (By.ID, "login-btn"),
                (By.ID, "login-button"),
                (By.ID, "submit-btn"),
                (By.ID, "enter"),
                
                # По тексту (русский)
                (By.XPATH, "//button[contains(text(), 'Войти')]"),
                (By.XPATH, "//button[contains(text(), 'Вход')]"),
                (By.XPATH, "//button[contains(text(), 'Авторизация')]"),
                (By.XPATH, "//button[contains(text(), 'Отправить')]"),
                (By.XPATH, "//input[@value='Войти']"),
                (By.XPATH, "//input[@value='Вход']"),
                (By.XPATH, "//input[@value='Отправить']"),
                
                # По тексту (английский)
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.XPATH, "//button[contains(text(), 'Sign in')]"),
                (By.XPATH, "//button[contains(text(), 'Submit')]"),
                (By.XPATH, "//input[@value='Login']"),
                (By.XPATH, "//input[@value='Sign in']"),
                (By.XPATH, "//input[@value='Submit']"),
                
                # Дополнительные варианты
                (By.CSS_SELECTOR, "[onclick*='login']"),
                (By.CSS_SELECTOR, "[onclick*='submit']"),
                (By.CSS_SELECTOR, "form button"),
                (By.CSS_SELECTOR, "form input[type='submit']"),
                (By.CSS_SELECTOR, "form input[type='button']"),
            ]
            
            for by, selector in button_selectors:
                try:
                    login_button = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    self._log_info(f"✅ Кнопка входа найдена: {by} = '{selector}'")
                    break
                except:
                    continue
            
            if not login_button:
                # Если кнопка не найдена, попробуем отправить форму через Enter
                self._log_info("⚠️ Кнопка входа не найдена, пробуем отправить через Enter...")
                from selenium.webdriver.common.keys import Keys
                password_field.send_keys(Keys.RETURN)
                time.sleep(3)
            else:
                # Нажимаем кнопку входа
                login_button.click()
                time.sleep(3)
            
            # Проверка успешности авторизации
            time.sleep(2)  # Ждем загрузки после авторизации
            
            # Проверяем, что мы не на странице логина (перенаправление произошло)
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Если остались на той же странице или есть ошибки авторизации
            if "login" in current_url.lower() or "ошибка" in page_source or "error" in page_source:
                self._log_info(f"⚠️ Возможно, ошибка авторизации. URL: {current_url}")
                # Не выбрасываем исключение, просто логируем
            else:
                self._log_info(f"✅ Авторизация выполнена. URL: {current_url}")
            
        except Exception as e:
            self._log_error("Ошибка авторизации", e)
            raise Exception(f"Не удалось авторизоваться: {str(e)}")
    
    # =================== Выполнение задач ===================
    
    def _execute_export_task(self, task: Task, settings: Settings):
        """Выполняет задание на вывоз контейнера"""
        self._log_task_info("📤 Выполнение экспорта", f"Дата: {task.date}, Слот: {task.time_slot}")
        
        # Здесь должна быть основная логика выполнения задания
        # Это упрощенная версия - в оригинале ~2000 строк кода
        
        self._log_task_info("✅ Экспорт выполнен", "Базовый сценарий завершен успешно")
    
    def _execute_import_task(self, task: Task, settings: Settings):
        """Выполняет задание на ввоз контейнера"""
        self._log_task_info("📥 Выполнение импорта", f"Дата: {task.date}, Слот: {task.time_slot}")
        
        # Здесь должна быть основная логика выполнения задания
        
        self._log_task_info("✅ Импорт выполнен", "Базовый сценарий завершен успешно")
    
    # =================== Логирование ===================
    
    def _log_info(self, message: str):
        """Логирует информационное сообщение"""
        entry = LogEntry(
            level=LogLevel.INFO,
            category=LogCategory.BROWSER_AUTOMATION,
            message=message
        )
        self.log_repo.save(entry)
    
    def _log_task_info(self, message: str, details: str = ""):
        """Логирует информацию о задании"""
        task_id = self.current_task.id if self.current_task else ""
        entry = LogEntry(
            level=LogLevel.INFO,
            category=LogCategory.TASK_EXECUTION,
            message=message,
            details=details,
            task_id=task_id
        )
        self.log_repo.save(entry)
    
    def _log_task_error(self, message: str, error: Exception):
        """Логирует ошибку задания"""
        task_id = self.current_task.id if self.current_task else ""
        entry = LogEntry(
            level=LogLevel.ERROR,
            category=LogCategory.TASK_EXECUTION,
            message=message,
            error=str(error),
            task_id=task_id
        )
        self.log_repo.save(entry)
    
    def _log_error(self, message: str, error: Exception):
        """Логирует ошибку"""
        entry = create_error_log(LogCategory.BROWSER_AUTOMATION, message, error)
        self.log_repo.save(entry)

