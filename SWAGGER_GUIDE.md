# Swagger API Documentation Guide

## Запуск сервера

```powershell
cd C:\Users\yokai\Downloads\rlisystems_v1\rlisystems_v1\python_version
.\venv\Scripts\Activate.ps1
python main.py
```

Сервер запускается на порту **8088**.

## Доступ к Swagger UI

Откройте в браузере:
- **Swagger UI**: http://localhost:8088/docs
- **ReDoc**: http://localhost:8088/redoc

## Доступные API Endpoints

### 1. Задания (Tasks)

#### GET `/api/tasks`
Получить список всех заданий
- **Response**: Массив объектов Task

#### POST `/api/tasks/create`
Создать новое задание
- **Body**: TaskCreate
- **Response**: SuccessResponse с ID созданного задания

#### PUT `/api/tasks/update`
Обновить существующее задание
- **Body**: TaskUpdate
- **Response**: SuccessResponse

#### DELETE `/api/tasks/delete?task_id={id}`
Удалить задание
- **Query Parameter**: task_id
- **Response**: SuccessResponse

#### POST `/api/tasks/reorder`
Изменить порядок заданий
- **Body**: TaskReorderRequest (словарь task_positions)
- **Response**: SuccessResponse

### 2. Настройки (Settings)

#### GET `/api/settings`
Получить текущие настройки
- **Response**: SettingsResponse

#### POST `/api/settings`
Обновить настройки
- **Body**: SettingsUpdate
- **Response**: SuccessResponse

### 3. Справочники (References)

#### GET `/api/references`
Получить все справочники
- **Response**: ReferencesResponse с полями:
  - operation_types
  - statuses
  - car_numbers
  - drivers
  - terminal_contracts
  - time_slots

#### POST `/api/references/add`
Добавить элемент в справочник
- **Body**: ReferenceAddRequest
  - type: operations/statuses/timeslots/autos/drivers/contracts
  - value: строка
  - description: строка (опционально)
- **Response**: SuccessResponse

#### DELETE `/api/references/delete`
Удалить элемент из справочника
- **Body**: ReferenceDeleteRequest
  - type: строка
  - itemId: строка
- **Response**: SuccessResponse

### 4. Логи (Logs)

#### GET `/api/logs`
Получить последние логи
- **Response**: Массив LogEntryResponse (последние 100 записей)

### 5. Автоматизация (Automation)

#### POST `/api/automation/start`
Запустить автоматизацию
- **Body**: AutomationStartRequest
  - taskIds: массив строк (ID заданий)
  - taskId: строка (для обратной совместимости, опционально)
  - parallel: boolean (параллельное выполнение)
  - maxConcurrency: integer (максимальная параллельность, по умолчанию 5)
- **Response**: AutomationResponse
- **Описание**: Запускает автоматизацию в фоновом потоке. Логи пишутся в систему логов.

#### POST `/api/automation/stop`
Остановить автоматизацию
- **Response**: AutomationResponse

### 6. Подключение (Connection)

#### POST `/api/connection/test`
Протестировать подключение
- **Body**: ConnectionTestRequest
  - site_url: строка
  - login: строка
  - password: строка
  - остальные параметры опциональны (см. SettingsUpdate)
- **Response**: ConnectionTestResponse
  - success: boolean
  - message: строка
  - error: строка
  - duration: integer (миллисекунды)
  - tested_at: строка

## Как использовать Swagger

1. Откройте http://localhost:8088/docs
2. Найдите нужный endpoint
3. Нажмите "Try it out"
4. Заполните параметры (если требуется)
5. Нажмите "Execute"
6. Посмотрите ответ сервера

## Автоматизация - особый случай

При запуске автоматизации через `/api/automation/start`:

1. **Запрос отправляется** → получаете `success: true`
2. **Автоматизация запускается в фоне**
3. **Все действия логируются** в `/api/logs`
4. **Проверяйте логи** для отслеживания прогресса

Пример последовательности:
```
1. POST /api/automation/start → {"success": true}
2. GET /api/logs → смотрите прогресс
3. GET /api/logs → проверяете результат
4. Если нужно - POST /api/automation/stop
```

## Примечания

- Все запросы возвращают JSON
- Ошибки возвращаются с соответствующими HTTP кодами
- Логи содержат подробную информацию о выполнении
- Автоматизация использует Selenium и может занять время

