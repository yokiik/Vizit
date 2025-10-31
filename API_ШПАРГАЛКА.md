# ⚡ API Шпаргалка - Быстрый справочник

## 🔗 Base URL
```
http://localhost:8088
```

---

## 📋 Задания (Tasks)

| Метод | Endpoint | Кнопка | Описание |
|-------|----------|--------|----------|
| `GET` | `/api/tasks` | Автозагрузка | Получить все задания |
| `POST` | `/api/tasks/create` | ➕ Добавить | Создать задание |
| `PUT` | `/api/tasks/update` | ✏️ Редактировать | Обновить задание |
| `DELETE` | `/api/tasks/delete?task_id={id}` | 🗑️ Удалить | Удалить задание |
| `POST` | `/api/tasks/reorder` | Drag & Drop | Изменить порядок |

---

## ⚙️ Настройки (Settings)

| Метод | Endpoint | Кнопка | Описание |
|-------|----------|--------|----------|
| `GET` | `/api/settings` | Автозагрузка | Получить настройки |
| `POST` | `/api/settings` | 💾 Сохранить | Обновить настройки |

---

## 📚 Справочники (References)

| Метод | Endpoint | Кнопка | Описание |
|-------|----------|--------|----------|
| `GET` | `/api/references` | Автозагрузка | Получить все справочники |
| `POST` | `/api/references/add` | ➕ Добавить | Добавить элемент |
| `DELETE` | `/api/references/delete` | 🗑️ Удалить | Удалить элемент |

**Типы справочников:**
- `operations` — Операции
- `statuses` — Статусы
- `timeslots` — Временные слоты
- `autos` — Автомобили
- `drivers` — Водители
- `contracts` — Договоры

---

## 📝 Логи (Logs)

| Метод | Endpoint | Обновление | Описание |
|-------|----------|------------|----------|
| `GET` | `/api/logs` | Каждые 5 сек | Получить логи (последние 100) |

---

## 🤖 Автоматизация (Automation)

| Метод | Endpoint | Кнопка | Описание |
|-------|----------|--------|----------|
| `POST` | `/api/automation/start` | 🚀 Поочередно / ⚡ Параллельно | Запустить задания |
| `POST` | `/api/automation/stop` | 🛑 Остановить | Остановить выполнение |

---

## 🔌 Подключение (Connection)

| Метод | Endpoint | Кнопка | Описание |
|-------|----------|--------|----------|
| `POST` | `/api/connection/test` | 🔌 Проверить | Тест подключения |

---

## 💡 Быстрые примеры

### Создать задание
```javascript
fetch('http://localhost:8088/api/tasks/create', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        type_task: "Ввоз",
        date: "25.10",
        time_slot: "09:00-12:00",
        num_auto: "А123БВ777",
        driver: "Иванов И.И.",
        status: "Новый"
    })
});
```

### Запустить автоматизацию
```javascript
fetch('http://localhost:8088/api/automation/start', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        taskIds: ["task-id-1", "task-id-2"],
        parallel: false
    })
});
```

### Добавить автомобиль
```javascript
fetch('http://localhost:8088/api/references/add', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        type: "autos",
        value: "А456ВГ199",
        description: ""
    })
});
```

---

## 🎨 ID элементов UI

### Кнопки управления заданиями
```
add-task-btn                    // ➕ Добавить задание
start-automation-sequential-btn // 🚀 Запустить поочередно
start-automation-parallel-btn   // ⚡ Запустить параллельно
stop-automation-btn             // 🛑 Остановить
```

### Кнопки настроек
```
test-connection-btn  // 🔌 Проверить подключение
save-settings-btn    // 💾 Сохранить настройки
```

### Кнопки справочников
```
add-reference-btn  // ➕ Добавить элемент
```

### Панель логов
```
log-level-filter     // Фильтр по уровню
log-category-filter  // Фильтр по категории
clear-logs-btn       // 🗑️ Очистить логи
logs-container       // Контейнер логов
```

### Формы
```
task-form       // Форма задания
settings-form   // Форма настроек
reference-form  // Форма справочника
```

### Модальные окна
```
task-modal       // Модальное окно задания
reference-modal  // Модальное окно справочника
```

---

## 🚨 Коды ошибок

| Код | Значение |
|-----|----------|
| `200` | ✅ Успех |
| `400` | ❌ Неверные данные |
| `404` | ❌ Не найдено |
| `409` | ⚠️ Конфликт (дубликат) |
| `500` | ❌ Ошибка сервера |

---

## 📚 Swagger
**http://localhost:8088/docs** — Интерактивная документация

---

**Полная документация:** `API_ДЛЯ_ФРОНТЕНДА.md`


