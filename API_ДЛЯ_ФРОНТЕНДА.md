# 📘 API Документация для фронтенд-разработчика

## 🎯 Общая информация

**Base URL:** `http://localhost:8088`  
**Документация Swagger:** `http://localhost:8088/docs`  
**Формат:** `application/json`

---

## 📑 Оглавление

1. [Задания (Tasks)](#1-задания-tasks)
2. [Настройки (Settings)](#2-настройки-settings)
3. [Справочники (References)](#3-справочники-references)
4. [Логи (Logs)](#4-логи-logs)
5. [Автоматизация (Automation)](#5-автоматизация-automation)
6. [Проверка подключения (Connection)](#6-проверка-подключения-connection)

---

## 1. Задания (Tasks)

### 1.1. Получить список заданий

**Метод:** `GET /api/tasks`  
**Кнопка:** Автоматическая загрузка при открытии вкладки "Задания"

**Запрос:**
```javascript
fetch('http://localhost:8088/api/tasks')
    .then(response => response.json())
    .then(data => console.log(data));
```

**Ответ:**
```json
[
    {
        "id": "uuid-1234-5678",
        "in_work": false,
        "type_task": "Ввоз",
        "status": "Новый",
        "date": "25.10",
        "time_slot": "09:00-12:00",
        "time_cancel": 30,
        "count_try": 60,
        "delay_try": 60,
        "num_auto": "А123БВ777",
        "driver": "Иванов Иван Иванович",
        "place": "Склад А",
        "index_container": "ABCD",
        "number_container": "1234567",
        "release_order": "ORD-123",
        "contract_terminal": "Договор №123",
        "created_at": "2024-10-30T12:00:00",
        "updated_at": "2024-10-30T12:00:00",
        "position": 1
    }
]
```

**Где разместить:**
- Функция: `loadTasks()` в `app.js`
- Вызывать при загрузке страницы и переключении на вкладку "Задания"

---

### 1.2. Создать новое задание

**Метод:** `POST /api/tasks/create`  
**Кнопка:** ➕ "Добавить задание" (кнопка `add-task-btn`)

**Запрос:**
```javascript
fetch('http://localhost:8088/api/tasks/create', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        type_task: "Ввоз",
        status: "Новый",
        date: "25.10",
        time_slot: "09:00-12:00",
        num_auto: "А123БВ777",
        driver: "Иванов Иван Иванович",
        place: "Склад А",
        index_container: "ABCD",
        number_container: "1234567",
        release_order: "ORD-123",
        contract_terminal: "Договор №123",
        time_cancel: 30,
        count_try: 60,
        delay_try: 60
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Ответ:**
```json
{
    "success": true,
    "message": "Задание создано с ID: uuid-1234-5678"
}
```

**Обязательные поля:**
- `type_task` — Тип операции (Ввоз/Вывоз)
- `date` — Дата в формате DD.MM
- `time_slot` — Временной слот
- `num_auto` — Номер автомобиля
- `driver` — ФИО водителя

**Где разместить:**
- Кнопка: ID `add-task-btn` (верхняя панель вкладки "Задания")
- Форма: Модальное окно с ID `task-modal`
- Функция: `saveTask()` в `app.js`

---

### 1.3. Обновить задание

**Метод:** `PUT /api/tasks/update`  
**Кнопка:** ✏️ "Редактировать" (кнопка рядом с каждым заданием)

**Запрос:**
```javascript
fetch('http://localhost:8088/api/tasks/update', {
    method: 'PUT',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        id: "uuid-1234-5678",
        in_work: false,
        type_task: "Ввоз",
        status: "Новый",
        date: "25.10",
        time_slot: "09:00-12:00",
        num_auto: "А123БВ777",
        driver: "Иванов Иван Иванович",
        place: "Склад А",
        index_container: "ABCD",
        number_container: "1234567",
        release_order: "ORD-123",
        contract_terminal: "Договор №123",
        time_cancel: 30,
        count_try: 60,
        delay_try: 60
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Ответ:**
```json
{
    "success": true,
    "message": null
}
```

**Где разместить:**
- Кнопка: ✏️ рядом с каждым заданием в списке
- Форма: То же модальное окно `task-modal` (но в режиме редактирования)
- Функция: `editTask(taskId)` и `saveTask()` в `app.js`

---

### 1.4. Удалить задание

**Метод:** `DELETE /api/tasks/delete?task_id={id}`  
**Кнопка:** 🗑️ "Удалить" (кнопка рядом с каждым заданием)

**Запрос:**
```javascript
const taskId = "uuid-1234-5678";
fetch(`http://localhost:8088/api/tasks/delete?task_id=${taskId}`, {
    method: 'DELETE'
})
.then(response => response.json())
.then(data => console.log(data));
```

**Ответ:**
```json
{
    "success": true,
    "message": null
}
```

**Где разместить:**
- Кнопка: 🗑️ рядом с каждым заданием в списке
- Функция: `deleteTask(taskId)` в `app.js`
- **Рекомендация:** Добавить подтверждение `confirm("Удалить задание?")`

---

### 1.5. Изменить порядок заданий

**Метод:** `POST /api/tasks/reorder`  
**Функция:** Drag & Drop (перетаскивание заданий мышью)

**Запрос:**
```javascript
fetch('http://localhost:8088/api/tasks/reorder', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        task_positions: {
            "uuid-1234-5678": 1,
            "uuid-8765-4321": 2,
            "uuid-1111-2222": 3
        }
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Ответ:**
```json
{
    "success": true,
    "message": null
}
```

**Где разместить:**
- Функция: `reorderTasks()` в `app.js`
- Событие: При перетаскивании задания в списке (Drag & Drop)
- **Библиотека:** Можно использовать SortableJS или встроенный HTML5 Drag & Drop

---

## 2. Настройки (Settings)

### 2.1. Получить настройки

**Метод:** `GET /api/settings`  
**Кнопка:** Автоматическая загрузка при открытии вкладки "Настройки"

**Запрос:**
```javascript
fetch('http://localhost:8088/api/settings')
    .then(response => response.json())
    .then(data => console.log(data));
```

**Ответ:**
```json
{
    "site_url": "https://example.com",
    "login": "user@example.com",
    "password": "password123",
    "refresh_interval": 30,
    "connection_status": false,
    "last_connection_test": null,
    "default_execution_attempts": 60,
    "default_delay_try": 60,
    "element_timeout": 10,
    "use_headless": false,
    "save_credentials": false,
    "browser_width": 1280,
    "browser_height": 720,
    "browser_path": "",
    "slot_check_attempts": 10,
    "slot_check_interval": 5,
    "created_at": "2024-10-30T12:00:00",
    "updated_at": "2024-10-30T12:00:00"
}
```

**Где разместить:**
- Функция: `loadSettings()` в `app.js`
- Вызывать при переключении на вкладку "Настройки"

---

### 2.2. Сохранить настройки

**Метод:** `POST /api/settings`  
**Кнопка:** 💾 "Сохранить настройки" (кнопка `save-settings-btn`)

**Запрос:**
```javascript
fetch('http://localhost:8088/api/settings', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        site_url: "https://example.com",
        login: "user@example.com",
        password: "password123",
        refresh_interval: 30,
        default_execution_attempts: 60,
        default_delay_try: 60,
        element_timeout: 10,
        use_headless: false,
        save_credentials: true,
        browser_width: 1280,
        browser_height: 720,
        browser_path: "",
        slot_check_attempts: 10,
        slot_check_interval: 5
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Ответ:**
```json
{
    "success": true,
    "message": null
}
```

**Обязательные поля:**
- `site_url` — URL сайта
- `login` — Логин
- `password` — Пароль

**Где разместить:**
- Кнопка: В форме настроек (после полей ввода)
- Форма: ID `settings-form`
- Функция: `saveSettings()` в `app.js`

---

## 3. Справочники (References)

### 3.1. Получить все справочники

**Метод:** `GET /api/references`  
**Кнопка:** Автоматическая загрузка при открытии вкладки "Справочники"

**Запрос:**
```javascript
fetch('http://localhost:8088/api/references')
    .then(response => response.json())
    .then(data => console.log(data));
```

**Ответ:**
```json
{
    "operation_types": [
        {
            "id": "uuid-op-1",
            "value": "Ввоз",
            "description": "Ввоз контейнеров",
            "is_active": true,
            "created_at": "2024-10-30T12:00:00",
            "updated_at": "2024-10-30T12:00:00"
        },
        {
            "id": "uuid-op-2",
            "value": "Вывоз",
            "description": "Вывоз контейнеров",
            "is_active": true,
            "created_at": "2024-10-30T12:00:00",
            "updated_at": "2024-10-30T12:00:00"
        }
    ],
    "statuses": [
        {
            "id": "uuid-st-1",
            "value": "Новый",
            "description": "Новое задание",
            "is_active": true,
            "created_at": "2024-10-30T12:00:00",
            "updated_at": "2024-10-30T12:00:00"
        }
    ],
    "car_numbers": [
        {
            "id": "uuid-car-1",
            "value": "А123БВ777",
            "description": "",
            "is_active": true,
            "created_at": "2024-10-30T12:00:00",
            "updated_at": "2024-10-30T12:00:00"
        }
    ],
    "drivers": [
        {
            "id": "uuid-drv-1",
            "value": "Иванов Иван Иванович",
            "description": "",
            "is_active": true,
            "created_at": "2024-10-30T12:00:00",
            "updated_at": "2024-10-30T12:00:00"
        }
    ],
    "terminal_contracts": [
        {
            "id": "uuid-cntr-1",
            "value": "Договор №123",
            "description": "",
            "is_active": true,
            "created_at": "2024-10-30T12:00:00",
            "updated_at": "2024-10-30T12:00:00"
        }
    ],
    "time_slots": [
        {
            "id": "uuid-time-1",
            "value": "09:00-12:00",
            "description": "",
            "is_active": true,
            "created_at": "2024-10-30T12:00:00",
            "updated_at": "2024-10-30T12:00:00"
        }
    ],
    "updated_at": "2024-10-30T12:00:00"
}
```

**Где разместить:**
- Функция: `loadReferences()` в `app.js`
- Вызывать при переключении на вкладку "Справочники"

---

### 3.2. Добавить элемент в справочник

**Метод:** `POST /api/references/add`  
**Кнопка:** ➕ "Добавить" (кнопка `add-reference-btn`)

**Запрос:**
```javascript
fetch('http://localhost:8088/api/references/add', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        type: "autos",  // operations, statuses, timeslots, autos, drivers, contracts
        value: "А456ВГ199",
        description: "Грузовой автомобиль"
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Ответ:**
```json
{
    "success": true,
    "message": "Элемент добавлен: uuid-new-item"
}
```

**Типы справочников:**
- `operations` — Типы операций (Ввоз/Вывоз)
- `statuses` — Статусы заданий
- `timeslots` — Временные слоты
- `autos` — Номера автомобилей
- `drivers` — Водители
- `contracts` — Договоры с терминалом

**Где разместить:**
- Кнопка: ➕ "Добавить" в каждой вкладке справочника
- Форма: Модальное окно для ввода значения и описания
- Функция: `saveReference()` в `app.js`

---

### 3.3. Удалить элемент из справочника

**Метод:** `DELETE /api/references/delete`  
**Кнопка:** 🗑️ "Удалить" (кнопка рядом с каждым элементом справочника)

**Запрос:**
```javascript
fetch('http://localhost:8088/api/references/delete', {
    method: 'DELETE',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        type: "autos",
        itemId: "uuid-car-1"
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Ответ:**
```json
{
    "success": true,
    "message": null
}
```

**Где разместить:**
- Кнопка: 🗑️ рядом с каждым элементом в списке справочника
- Функция: `deleteReference(type, itemId)` в `app.js`

---

## 4. Логи (Logs)

### 4.1. Получить логи

**Метод:** `GET /api/logs`  
**Кнопка:** Автоматическая загрузка каждые 5 секунд

**Запрос:**
```javascript
fetch('http://localhost:8088/api/logs')
    .then(response => response.json())
    .then(data => console.log(data));
```

**Ответ:**
```json
[
    {
        "id": "uuid-log-1",
        "timestamp": "2024-10-30T12:00:00",
        "level": "INFO",
        "category": "SYSTEM",
        "message": "Приложение запущено",
        "details": "",
        "task_id": "",
        "user_action": false,
        "error": ""
    },
    {
        "id": "uuid-log-2",
        "timestamp": "2024-10-30T12:01:00",
        "level": "WARNING",
        "category": "BROWSER_AUTOMATION",
        "message": "Браузер не найден",
        "details": "Chrome не установлен",
        "task_id": "",
        "user_action": false,
        "error": "Chrome not found"
    }
]
```

**Уровни логов (level):**
- `DEBUG` — Отладочная информация
- `INFO` — Информационные сообщения
- `WARNING` — Предупреждения
- `ERROR` — Ошибки
- `CRITICAL` — Критические ошибки

**Категории (category):**
- `SYSTEM` — Системные сообщения
- `BROWSER_AUTOMATION` — Автоматизация браузера
- `USER_ACTION` — Действия пользователя
- `DATA_STORAGE` — Работа с данными

**Где разместить:**
- Панель: Правая панель приложения (ID `logs-container`)
- Функция: `loadLogs()` в `app.js`
- **Автообновление:** `setInterval(loadLogs, 5000)` — каждые 5 секунд
- **Фильтры:** 
  - По уровню (ID `log-level-filter`)
  - По категории (ID `log-category-filter`)

---

## 5. Автоматизация (Automation)

### 5.1. Запустить автоматизацию

**Метод:** `POST /api/automation/start`  
**Кнопки:** 
- 🚀 "Запустить поочередно" (ID `start-automation-sequential-btn`)
- ⚡ "Запустить параллельно" (ID `start-automation-parallel-btn`)

**Запрос (последовательный запуск):**
```javascript
fetch('http://localhost:8088/api/automation/start', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        taskIds: ["uuid-task-1", "uuid-task-2", "uuid-task-3"],
        parallel: false
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Запрос (параллельный запуск):**
```javascript
fetch('http://localhost:8088/api/automation/start', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        taskIds: ["uuid-task-1", "uuid-task-2", "uuid-task-3"],
        parallel: true,
        maxConcurrency: 5  // Максимум 5 заданий одновременно
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Ответ:**
```json
{
    "success": true,
    "message": null
}
```

**Где разместить:**
- Кнопки: Верхняя панель вкладки "Задания"
  - 🚀 "Запустить поочередно" — `start-automation-sequential-btn`
  - ⚡ "Запустить параллельно" — `start-automation-parallel-btn`
- Функция: `startAutomation(parallel)` в `app.js`

**Параметры:**
- `taskIds` — Массив ID заданий для выполнения
- `parallel` — `true` для параллельного выполнения, `false` для последовательного
- `maxConcurrency` — Количество одновременных заданий (по умолчанию 5)

---

### 5.2. Остановить автоматизацию

**Метод:** `POST /api/automation/stop`  
**Кнопка:** 🛑 "Остановить" (ID `stop-automation-btn`)

**Запрос:**
```javascript
fetch('http://localhost:8088/api/automation/stop', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    }
})
.then(response => response.json())
.then(data => console.log(data));
```

**Ответ:**
```json
{
    "success": true,
    "message": null
}
```

**Где разместить:**
- Кнопка: 🛑 "Остановить" в верхней панели (ID `stop-automation-btn`)
- Функция: `stopAutomation()` в `app.js`

---

## 6. Проверка подключения (Connection)

### 6.1. Проверить подключение

**Метод:** `POST /api/connection/test`  
**Кнопка:** 🔌 "Проверить подключение" (ID `test-connection-btn`)

**Запрос:**
```javascript
fetch('http://localhost:8088/api/connection/test', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        site_url: "https://example.com",
        login: "user@example.com",
        password: "password123"
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Ответ (успех):**
```json
{
    "success": true,
    "message": "Подключение успешно!",
    "error": "",
    "duration": 1234,
    "tested_at": "2024-10-30T12:00:00"
}
```

**Ответ (ошибка):**
```json
{
    "success": false,
    "message": "Не удалось подключиться",
    "error": "Неверный логин или пароль",
    "duration": 5000,
    "tested_at": "2024-10-30T12:00:00"
}
```

**Где разместить:**
- Кнопка: 🔌 "Проверить подключение" в форме настроек (ID `test-connection-btn`)
- Функция: `testConnection()` в `app.js`
- **Индикатор:** Показывать статус подключения (успех/ошибка) рядом с кнопкой

---

## 🎨 Структура UI элементов

### Вкладка "Задания"

```
┌─────────────────────────────────────────────────┐
│  [➕ Добавить задание]  [🚀 Поочередно]         │
│  [⚡ Параллельно]  [🛑 Остановить]              │
├─────────────────────────────────────────────────┤
│  Список заданий:                                │
│  ┌───────────────────────────────────────┐      │
│  │ 📦 Ввоз | А123БВ777 | 25.10           │      │
│  │ Иванов И.И. | 09:00-12:00             │      │
│  │ [▶ Запустить] [✏️ Редактировать] [🗑️]  │      │
│  └───────────────────────────────────────┘      │
└─────────────────────────────────────────────────┘
```

**Кнопки:**
- `add-task-btn` — ➕ "Добавить задание"
- `start-automation-sequential-btn` — 🚀 "Запустить поочередно"
- `start-automation-parallel-btn` — ⚡ "Запустить параллельно"
- `stop-automation-btn` — 🛑 "Остановить"
- На каждом задании:
  - `▶ Запустить` — запуск одного задания
  - `✏️ Редактировать` — открыть модальное окно для редактирования
  - `🗑️ Удалить` — удалить задание

---

### Вкладка "Настройки"

```
┌─────────────────────────────────────────────────┐
│  Настройки подключения:                         │
│  URL сайта: [_____________________________]     │
│  Логин:     [_____________________________]     │
│  Пароль:    [_____________________________]     │
│  [🔌 Проверить подключение]                      │
│                                                  │
│  Настройки браузера:                            │
│  [ ] Headless режим                             │
│  [ ] Сохранять логин и пароль                   │
│                                                  │
│  [💾 Сохранить настройки]                        │
└─────────────────────────────────────────────────┘
```

**Кнопки:**
- `test-connection-btn` — 🔌 "Проверить подключение"
- `save-settings-btn` — 💾 "Сохранить настройки"

---

### Вкладка "Справочники"

```
┌─────────────────────────────────────────────────┐
│  [Операции] [Статусы] [Слоты] [Авто] [...]      │
├─────────────────────────────────────────────────┤
│  [➕ Добавить]                                   │
│                                                  │
│  Список элементов:                              │
│  ┌───────────────────────────────────────┐      │
│  │ А123БВ777  [🗑️ Удалить]               │      │
│  │ А456ВГ199  [🗑️ Удалить]               │      │
│  └───────────────────────────────────────┘      │
└─────────────────────────────────────────────────┘
```

**Кнопки:**
- `add-reference-btn` — ➕ "Добавить"
- На каждом элементе:
  - `🗑️ Удалить` — удалить элемент

---

### Панель логов (правая часть)

```
┌─────────────────────────────────────────────────┐
│  Фильтр: [Все уровни ▼] [Все категории ▼]      │
│  [🗑️ Очистить]                                  │
├─────────────────────────────────────────────────┤
│  12:00:00 | INFO | SYSTEM                       │
│  Приложение запущено                            │
│                                                  │
│  12:01:00 | WARNING | BROWSER                   │
│  Браузер не найден                              │
└─────────────────────────────────────────────────┘
```

**Элементы:**
- `log-level-filter` — Фильтр по уровню (dropdown)
- `log-category-filter` — Фильтр по категории (dropdown)
- `clear-logs-btn` — 🗑️ "Очистить" (очистка визуального отображения)

---

## 📦 Примеры полных функций для фронтенда

### Пример 1: Загрузка заданий

```javascript
async function loadTasks() {
    try {
        const response = await fetch('http://localhost:8088/api/tasks');
        if (!response.ok) throw new Error('Ошибка загрузки заданий');
        
        const tasks = await response.json();
        currentTasks = tasks;
        renderTasks(tasks);
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка загрузки заданий', 'error');
    }
}
```

---

### Пример 2: Создание задания

```javascript
async function createTask(taskData) {
    try {
        const response = await fetch('http://localhost:8088/api/tasks/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(taskData)
        });
        
        if (!response.ok) throw new Error('Ошибка создания задания');
        
        const result = await response.json();
        showNotification(result.message || 'Задание создано', 'success');
        await loadTasks();  // Обновить список
        closeTaskModal();
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка создания задания', 'error');
    }
}
```

---

### Пример 3: Запуск автоматизации

```javascript
async function startAutomation(parallel = false) {
    // Получить ID выбранных заданий
    const selectedTasks = currentTasks
        .filter(task => !task.in_work)  // Только не запущенные
        .map(task => task.id);
    
    if (selectedTasks.length === 0) {
        showNotification('Нет заданий для запуска', 'warning');
        return;
    }
    
    try {
        const response = await fetch('http://localhost:8088/api/automation/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                taskIds: selectedTasks,
                parallel: parallel,
                maxConcurrency: 5
            })
        });
        
        if (!response.ok) throw new Error('Ошибка запуска автоматизации');
        
        const result = await response.json();
        const mode = parallel ? 'параллельно' : 'поочередно';
        showNotification(`Автоматизация запущена ${mode}`, 'success');
        
        // Начать периодическое обновление
        startAutoRefresh();
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка запуска автоматизации', 'error');
    }
}
```

---

### Пример 4: Добавление элемента в справочник

```javascript
async function addReference(type, value, description = '') {
    try {
        const response = await fetch('http://localhost:8088/api/references/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: type,
                value: value,
                description: description
            })
        });
        
        if (!response.ok) {
            if (response.status === 409) {
                throw new Error('Такой элемент уже существует');
            }
            throw new Error('Ошибка добавления');
        }
        
        const result = await response.json();
        showNotification(result.message || 'Элемент добавлен', 'success');
        await loadReferences();  // Обновить справочники
        closeReferenceModal();
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification(error.message, 'error');
    }
}
```

---

### Пример 5: Проверка подключения

```javascript
async function testConnection() {
    const siteUrl = document.getElementById('site-url').value;
    const login = document.getElementById('login').value;
    const password = document.getElementById('password').value;
    
    if (!siteUrl || !login || !password) {
        showNotification('Заполните все поля', 'warning');
        return;
    }
    
    // Показать индикатор загрузки
    const btn = document.getElementById('test-connection-btn');
    btn.disabled = true;
    btn.textContent = '🔄 Проверка...';
    
    try {
        const response = await fetch('http://localhost:8088/api/connection/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                site_url: siteUrl,
                login: login,
                password: password
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`✅ ${result.message} (${result.duration}ms)`, 'success');
        } else {
            showNotification(`❌ ${result.message}: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка проверки подключения', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = '🔌 Проверить подключение';
    }
}
```

---

## 🚨 Обработка ошибок

Все API endpoints могут возвращать ошибки в следующем формате:

```json
{
    "detail": "Описание ошибки"
}
```

**HTTP коды ошибок:**
- `400` — Неверные данные запроса
- `404` — Ресурс не найден
- `409` — Конфликт (например, дубликат)
- `500` — Внутренняя ошибка сервера

**Пример обработки:**
```javascript
try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Произошла ошибка');
    }
    
    const data = await response.json();
    // Обработка успешного ответа
} catch (error) {
    console.error('Ошибка:', error);
    showNotification(error.message, 'error');
}
```

---

## 📊 Периодическое обновление данных

Рекомендуется настроить автоматическое обновление для:

### Логи (каждые 3-5 секунд)
```javascript
setInterval(async () => {
    await loadLogs();
}, 5000);
```

### Задания (каждые 10 секунд, когда запущена автоматизация)
```javascript
let autoRefreshInterval = null;

function startAutoRefresh() {
    if (autoRefreshInterval) return;
    autoRefreshInterval = setInterval(async () => {
        await loadTasks();
    }, 10000);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}
```

---

## 🎯 Чеклист интеграции

### Вкладка "Задания"
- [ ] Кнопка "Добавить задание" → `POST /api/tasks/create`
- [ ] Кнопка "Редактировать" → `PUT /api/tasks/update`
- [ ] Кнопка "Удалить" → `DELETE /api/tasks/delete`
- [ ] Кнопка "Запустить поочередно" → `POST /api/automation/start` (parallel=false)
- [ ] Кнопка "Запустить параллельно" → `POST /api/automation/start` (parallel=true)
- [ ] Кнопка "Остановить" → `POST /api/automation/stop`
- [ ] Drag & Drop → `POST /api/tasks/reorder`
- [ ] Загрузка заданий при открытии → `GET /api/tasks`

### Вкладка "Настройки"
- [ ] Загрузка настроек → `GET /api/settings`
- [ ] Кнопка "Сохранить" → `POST /api/settings`
- [ ] Кнопка "Проверить подключение" → `POST /api/connection/test`

### Вкладка "Справочники"
- [ ] Загрузка справочников → `GET /api/references`
- [ ] Кнопка "Добавить" → `POST /api/references/add`
- [ ] Кнопка "Удалить" → `DELETE /api/references/delete`

### Панель логов
- [ ] Загрузка логов → `GET /api/logs`
- [ ] Автообновление каждые 5 секунд
- [ ] Фильтрация по уровню
- [ ] Фильтрация по категории

---

## 📞 Дополнительная информация

**Swagger документация:** http://localhost:8088/docs  
**ReDoc документация:** http://localhost:8088/redoc

В Swagger можно:
- 🧪 Протестировать каждый endpoint
- 📖 Посмотреть полные схемы данных
- 🔍 Увидеть все возможные параметры

---

**Дата создания:** Октябрь 2024  
**Версия:** 1.0  
**Автор:** RLI Systems Team

🎉 **Успешной интеграции!**


