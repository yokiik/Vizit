# ⚡ Swagger - Быстрый старт (2 минуты)

## 🎯 Цель
Запустить API на сервере и открыть Swagger UI для тестирования методов.

---

## 📋 Быстрая инструкция

### 1. Подключитесь к серверу
```bash
ssh root@ВАШ_IP_СЕРВЕРА
```

### 2. Клонируйте репозиторий
```bash
cd /tmp
git clone https://github.com/yokiik/Vizit.git
cd Vizit/python_version
```

### 3. Установите зависимости
```bash
# Установите Python (если нужно)
sudo apt update && sudo apt install python3 python3-pip python3-venv -y

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите пакеты
pip install -r requirements.txt
```

### 4. Запустите приложение
```bash
python3 main.py
```

Вы увидите:
```
=== RLI Systems Python Version ===
Starting web interface...
[OK] Data storage initialized
[OK] Business services created
[INFO] Starting server on port 8088
[INFO] Open browser: http://localhost:8088
[INFO] Swagger docs: http://localhost:8088/docs
Press Ctrl+C to stop
```

### 5. Откройте Swagger в браузере

```
http://ВАШ_IP_СЕРВЕРА:8088/docs
```

**Пример:** `http://123.45.67.89:8088/docs`

---

## ✅ Готово!

Теперь в браузере:
1. Видите все API методы
2. Нажимайте "Try it out" на любом методе
3. Заполняйте параметры
4. Нажимайте "Execute"
5. Видите результат

---

## 🔥 Если не открывается

### Проблема: порт закрыт файрволом

```bash
# Откройте порт 8088
sudo ufw allow 8088/tcp
sudo ufw status
```

### Проблема: приложение не запустилось

```bash
# Проверьте логи
python3 main.py

# Или запустите на другом порту
PORT=8000 python3 main.py
```

---

## 📖 Основные методы API

После открытия Swagger UI вы увидите:

### 🔵 GET методы (чтение данных)
- `GET /api/tasks` - список заданий
- `GET /api/settings` - настройки
- `GET /api/references` - справочники
- `GET /api/logs` - логи

### 🟢 POST методы (создание/запуск)
- `POST /api/tasks/create` - создать задание
- `POST /api/automation/start` - запустить автоматизацию
- `POST /api/connection/test` - тест подключения

### 🟡 PUT методы (обновление)
- `PUT /api/tasks/update` - обновить задание

### 🔴 DELETE методы (удаление)
- `DELETE /api/tasks/delete` - удалить задание
- `DELETE /api/references/delete` - удалить из справочника

---

## 🎮 Как тестировать методы

### Пример 1: Получить список заданий

1. Найдите метод `GET /api/tasks`
2. Нажмите на него
3. Нажмите **"Try it out"**
4. Нажмите **"Execute"**
5. Увидите результат:
```json
[
  {
    "id": "uuid-here",
    "type_task": "Ввоз",
    "status": "Новое",
    "date": "2025-10-31",
    ...
  }
]
```

### Пример 2: Создать задание

1. Найдите метод `POST /api/tasks/create`
2. Нажмите **"Try it out"**
3. Отредактируйте JSON в поле Request body:
```json
{
  "type_task": "Ввоз",
  "status": "Новое",
  "date": "2025-11-01",
  "time_slot": "09:00-12:00",
  "num_auto": "А123ВС777",
  "driver": "Иванов И.И.",
  "place": "Терминал 1",
  "index_container": "A",
  "number_container": "ABCD1234567",
  "release_order": "ORD-123",
  "contract_terminal": "Договор №1"
}
```
4. Нажмите **"Execute"**
5. Увидите подтверждение создания

### Пример 3: Тест подключения

1. Найдите метод `POST /api/connection/test`
2. Нажмите **"Try it out"**
3. Заполните данные:
```json
{
  "site_url": "https://example.com",
  "login": "your_login",
  "password": "your_password"
}
```
4. Нажмите **"Execute"**
5. Увидите результат теста подключения

---

## 🛑 Остановить приложение

```bash
# В терминале где запущено приложение нажмите
Ctrl + C
```

---

## 🔄 Обновить код и перезапустить

```bash
cd /tmp/Vizit/python_version
git pull
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

---

## 🚀 Для постоянной работы (systemd)

Если хотите, чтобы приложение работало постоянно и перезапускалось автоматически:

```bash
# Скопируйте проект в постоянную директорию
sudo mkdir -p /var/www/apps
sudo cp -r /tmp/Vizit /var/www/apps/rli-systems
cd /var/www/apps/rli-systems/python_version

# Настройте systemd сервис
sudo cp systemd/rli-systems.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rli-systems.service
sudo systemctl start rli-systems.service

# Проверьте статус
sudo systemctl status rli-systems.service
```

Теперь приложение работает в фоне, и Swagger доступен 24/7!

---

## 📱 Альтернативные адреса

После запуска доступны:

| Адрес | Описание |
|-------|----------|
| `http://IP:8088/` | Главная страница (веб-интерфейс) |
| `http://IP:8088/docs` | Swagger UI (интерактивная документация) |
| `http://IP:8088/redoc` | ReDoc (альтернативная документация) |
| `http://IP:8088/api/tasks` | API endpoint (JSON ответ) |

---

## 💡 Полезные команды

```bash
# Проверить, запущено ли приложение
ps aux | grep python | grep main.py

# Проверить, какой процесс использует порт 8088
sudo netstat -tlnp | grep 8088

# Проверить доступность API
curl http://localhost:8088/api/tasks

# Просмотреть логи (если используется systemd)
sudo journalctl -u rli-systems.service -f
```

---

## ✅ Что дальше?

После успешного запуска:

1. ✅ Протестируйте все методы через Swagger UI
2. ✅ Настройте автоматический деплой (см. `БЫСТРЫЙ_ЗАПУСК_НА_СЕРВЕРЕ.md`)
3. ✅ Настройте Nginx для работы через домен
4. ✅ Добавьте HTTPS сертификат (Let's Encrypt)

---

## 📞 Нужна помощь?

Смотрите подробные инструкции:
- **БЫСТРЫЙ_ЗАПУСК_НА_СЕРВЕРЕ.md** - полная инструкция по развертыванию
- **DEPLOYMENT_GUIDE.md** - руководство по автоматизации деплоя
- **API_ДЛЯ_ФРОНТЕНДА.md** - документация всех методов API

---

**🎉 Приятного тестирования!**

