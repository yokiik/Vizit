# 📋 Руководство по работе системы автоматического деплоя - RLI Systems

## 🔄 Общая схема работы

Проект использует **CI/CD (Continuous Integration/Continuous Deployment)** через **GitHub Actions**. При каждом коммите в репозиторий автоматически запускается процесс деплоя на сервер.

---

## 1. 🎯 Триггер деплоя (GitHub Actions)

Когда разработчик делает `git push` в репозиторий, срабатывают GitHub Actions workflow'ы:

### Для Production (ветка main/master)
**Файл**: `.github/workflows/deploy.yml`

### Для Development (ветка dev)
**Файл**: `.github/workflows/deploy-dev.yml`

### Что происходит при push:

1. **Триггер** ⚡
   - GitHub обнаруживает push в ветку `main`, `master` или `dev`
   - Автоматически запускается соответствующий workflow

2. **Checkout кода** 📥
   - Скачивается код из репозитория
   - Используется `actions/checkout@v4` с полной историей коммитов

3. **Сбор информации о коммите** 📊
   ```bash
   git rev-parse HEAD              # Полный hash коммита
   git log -1 --pretty=%B          # Сообщение коммита
   git rev-parse --short=7 HEAD   # Короткий hash (7 символов)
   git log -1 --pretty=%an        # Автор коммита
   ```

4. **SSH подключение к серверу** 🔐
   - GitHub Actions подключается к VDS серверу
   - Использует SSH ключ из GitHub Secrets
   - Плагин: `appleboy/ssh-action@master`

5. **Запуск деплоя на сервере** 🚀
   ```bash
   # Production
   cd /var/www/apps/rlisystems_v1/python_version
   bash update.sh
   sudo systemctl restart rli-systems.service
   
   # Development
   cd /var/www/apps/rlisystems_v1/python_version-dev
   bash update.sh
   sudo systemctl restart rli-systems-dev.service
   ```

6. **Отображение результата** ✅
   - При успехе: сообщение с деталями деплоя
   - При ошибке: сообщение об ошибке в GitHub Actions

---

## 2. 📜 Скрипт обновления (update.sh)

**Расположение**: `/var/www/apps/rlisystems_v1/python_version/update.sh`

### Содержимое скрипта:

```bash
git fetch                           # 1. Загрузка изменений из удаленного репозитория
git reset --hard origin/main        # 2. ЖЕСТКИЙ сброс локальных изменений
git pull                            # 3. Применение изменений из удаленного репозитория
source venv/bin/activate            # 4. Активация виртуального окружения Python
pip install -r ./requirements.txt   # 5. Установка/обновление зависимостей Python
```

### Построчное объяснение:

#### Строка 1: `git fetch`
- **Что делает**: Загружает все изменения из удаленного репозитория (GitHub)
- **Важно**: НЕ применяет изменения, только скачивает их
- **Зачем**: Синхронизация с удаленным репозиторием

#### Строка 2: `git reset --hard origin/main`
- **Что делает**: ПОЛНОСТЬЮ удаляет все локальные изменения и синхронизирует с удаленной веткой
- **ВНИМАНИЕ**: Это НЕОБРАТИМАЯ операция!
- **Зачем**: 
  - Гарантирует, что код на сервере идентичен коду в репозитории
  - Удаляет любые случайные изменения на сервере
  - Предотвращает конфликты при `git pull`

#### Строка 3: `git pull`
- **Что делает**: Применяет загруженные изменения
- **Результат**: Код на сервере полностью обновляется до последней версии
- **Зачем**: Получение актуального кода из репозитория

#### Строка 4: `source venv/bin/activate`
- **Что делает**: Активирует виртуальное окружение Python
- **Важно**: Все Python команды после этого выполняются в venv
- **Зачем**: Изоляция зависимостей проекта от системного Python

#### Строка 5: `pip install -r ./requirements.txt`
- **Что делает**: Устанавливает/обновляет все зависимости Python
- **Важно**: Устанавливает только недостающие или измененные пакеты
- **Зачем**: 
  - Обновление библиотек до актуальных версий
  - Установка новых зависимостей, если они добавлены
  - Гарантия совместимости с кодом

---

## 3. 🔄 Перезапуск сервисов (systemd)

После выполнения `update.sh` GitHub Actions перезапускает systemd сервис.

### Что такое systemd?
**systemd** - это система инициализации и управления сервисами в Linux.

### Команда перезапуска:

```bash
sudo systemctl restart rli-systems.service  # Основное приложение (FastAPI)
```

### Почему сервер перезагружается автоматически?

1. **Python не перезагружает модули автоматически**
   - Изменения в коде не применяются в работающем процессе
   - Нужен полный перезапуск процесса

2. **systemctl restart делает "graceful restart":**
   - Останавливает старый процесс
   - Освобождает ресурсы (память, порты)
   - Запускает новый процесс с обновленным кодом
   - Применяет все изменения

3. **Без перезапуска:**
   - Новый код не применится
   - Сервер будет работать на старой версии

### Процесс перезапуска:

```
Старый процесс (PID 1234)
  ↓
systemctl restart rli-systems.service
  ↓
Graceful shutdown:
  - Завершаются текущие запросы
  - Останавливается Uvicorn сервер
  ↓
Процесс завершен
  ↓
Новый процесс (PID 5678)
  ↓
Запуск с новым кодом:
  - Читается обновленный код
  - Инициализируется FastAPI приложение
  - Запускается Uvicorn на порту 8088
  ↓
Сервер готов к работе!
```

---

## 4. 🏗️ Структура приложения (main.py)

### Ключевые компоненты:

#### FastAPI приложение
- **Файл**: `web/server.py`
- **Запуск**: через Uvicorn ASGI сервер
- **Порт**: 8088 (по умолчанию, настраивается через переменную окружения PORT)

#### Хранилище данных
- **Тип**: JSON файлы
- **Расположение**: `~/.rlisystems_python/`
- **Файлы**: `tasks.json`, `settings.json`, `references.json`, `logs.json`

#### Автоматизация браузера
- **Selenium WebDriver**: для автоматизации Chrome/Chromium
- **Webdriver Manager**: автоматическая установка ChromeDriver

---

## 5. ⚙️ Конфигурация

### Переменные окружения:

#### Настройки приложения
```bash
PORT=8088  # Порт для веб-сервера (по умолчанию 8088)
```

### Структура данных:
- Все данные хранятся в JSON файлах в домашней директории пользователя
- Путь: `~/.rlisystems_python/`
- Не требует внешних баз данных

---

## 6. 🔐 GitHub Secrets

Для работы автоматического деплоя нужно добавить секреты в GitHub:

**Путь**: Репозиторий → Settings → Secrets and variables → Actions → New repository secret

### Необходимые секреты:

| Имя секрета | Описание | Пример значения |
|-------------|----------|-----------------|
| `VDS_HOST` | IP адрес или домен сервера | `123.45.67.89` или `server.example.com` |
| `VDS_USERNAME` | Имя пользователя SSH | `root` или `www-data` |
| `VDS_SSH_KEY` | Приватный SSH ключ | Содержимое файла `~/.ssh/id_rsa` |

### Как получить SSH ключ:

```bash
# На вашем компьютере или на сервере
cat ~/.ssh/id_rsa

# Или создать новый ключ
ssh-keygen -t rsa -b 4096 -C "github-actions"
```

**Важно**: 
- Скопируйте **приватный** ключ (`id_rsa`) в `VDS_SSH_KEY`
- Добавьте **публичный** ключ (`id_rsa.pub`) на сервер в `~/.ssh/authorized_keys`

---

## 7. 🚀 Две среды деплоя

Проект поддерживает два окружения: Production и Development.

### Production (боевой сервер)

**Ветка Git**: `main` или `master`  
**Workflow**: `.github/workflows/deploy.yml`  
**Папка на сервере**: `/var/www/apps/rlisystems_v1/python_version`  
**Systemd сервис**: `rli-systems.service`

**Команды управления**:
```bash
# Проверка статуса
sudo systemctl status rli-systems.service

# Просмотр логов
sudo journalctl -u rli-systems.service -f

# Перезапуск
sudo systemctl restart rli-systems.service

# Остановка/запуск
sudo systemctl stop rli-systems.service
sudo systemctl start rli-systems.service
```

### Development (тестовый сервер)

**Ветка Git**: `dev` или `develop`  
**Workflow**: `.github/workflows/deploy-dev.yml`  
**Папка на сервере**: `/var/www/apps/rlisystems_v1/python_version-dev`  
**Systemd сервис**: `rli-systems-dev.service`

**Зачем нужны две среды:**
- Тестирование изменений перед продакшеном
- Изоляция от пользователей
- Безопасное тестирование новых функций

---

## 8. 📊 Полная диаграмма процесса деплоя

```
┌─────────────────────────────────────────────────────────────┐
│  1. РАЗРАБОТЧИК                                              │
│     git add .                                                │
│     git commit -m "Add new feature"                          │
│     git push origin main                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  2. GITHUB обнаруживает push в ветку main                   │
│     Триггер: on.push.branches = ["main", "master"]          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  3. GITHUB ACTIONS запускается                              │
│     - Checkout code (actions/checkout@v4)                   │
│     - Get commit info (hash, author, message)               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  4. SSH ПОДКЛЮЧЕНИЕ к серверу                               │
│     host: ${{ secrets.VDS_HOST }}                           │
│     username: ${{ secrets.VDS_USERNAME }}                   │
│     key: ${{ secrets.VDS_SSH_KEY }}                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  5. ВЫПОЛНЕНИЕ update.sh                                    │
│                                                              │
│     5.1. git fetch                                          │
│          └─ Загрузка изменений из GitHub                    │
│                                                              │
│     5.2. git reset --hard origin/main                        │
│          └─ Удаление локальных изменений                    │
│                                                              │
│     5.3. git pull                                           │
│          └─ Применение новых изменений                      │
│                                                              │
│     5.4. source venv/bin/activate                           │
│          └─ Активация Python окружения                      │
│                                                              │
│     5.5. pip install -r requirements.txt                    │
│          └─ Обновление зависимостей                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  6. ПЕРЕЗАПУСК СЕРВИСА                                      │
│                                                              │
│     sudo systemctl restart rli-systems.service              │
│          ├─ Остановка старого процесса                       │
│          ├─ Освобождение ресурсов                            │
│          ├─ Запуск нового процесса                          │
│          └─ Инициализация FastAPI приложения                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  7. РЕЗУЛЬТАТ ДЕПЛОЯ                                        │
│                                                              │
│     ✅ УСПЕХ:                                                │
│     🚀 Деплой успешно завершен!                              │
│     Окружение: PRODUCTION                                   │
│     Статус: Успешно развернуто                              │
│     Ветка: main                                             │
│     Коммит: a1b2c3d                                         │
│     Автор: Developer Name                                   │
│     Сообщение: Add new feature                              │
│                                                              │
│     ❌ ОШИБКА:                                               │
│     💥 Деплой завершился с ошибкой!                         │
│     Требуется внимание разработчиков!                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. 📝 Зависимости проекта (requirements.txt)

### Основные библиотеки:

#### Web Framework
- `fastapi` - Современный асинхронный web-фреймворк
- `uvicorn[standard]` - ASGI сервер для запуска FastAPI
- `pydantic` - Валидация данных
- `python-multipart` - Обработка multipart/form-data
- `jinja2` - Шаблонизация HTML

#### Автоматизация браузера
- `selenium` - WebDriver для автоматизации браузера
- `webdriver-manager` - Автоматическая установка ChromeDriver
- `beautifulsoup4` - Парсинг HTML

#### Утилиты
- `python-dateutil` - Работа с датами

---

## 10. 🔧 Настройка systemd сервисов

### Пример конфигурации rli-systems.service:

```ini
[Unit]
Description=RLI Systems Python Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/apps/rlisystems_v1/python_version
Environment="PATH=/var/www/apps/rlisystems_v1/python_version/venv/bin"
Environment="PYTHONUNBUFFERED=1"
Environment="PORT=8088"

ExecStart=/var/www/apps/rlisystems_v1/python_version/venv/bin/uvicorn \
    --host 127.0.0.1 \
    --port 8088 \
    --workers 4 \
    --log-level info \
    wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Расположение**: `/etc/systemd/system/rli-systems.service`

### Команды управления:

```bash
# Перезагрузка конфигурации после изменений
sudo systemctl daemon-reload

# Включить автозапуск при загрузке системы
sudo systemctl enable rli-systems.service

# Запустить сервис
sudo systemctl start rli-systems.service

# Перезапустить сервис
sudo systemctl restart rli-systems.service

# Проверить статус
sudo systemctl status rli-systems.service

# Просмотреть логи
sudo journalctl -u rli-systems.service -f

# Просмотреть последние 100 строк логов
sudo journalctl -u rli-systems.service -n 100
```

---

## 11. ❓ Часто задаваемые вопросы (FAQ)

### ❓ Почему сервер перезагружается автоматически после коммита?

**Ответ**: 
1. GitHub Actions отслеживает push в ветку `main` или `master`
2. Автоматически запускается workflow
3. В конце workflow явно вызывается `sudo systemctl restart rli-systems.service`
4. Это гарантирует, что новый код применится немедленно

### ❓ Зачем нужен `git reset --hard`?

**Ответ**:
- Удаляет ВСЕ локальные изменения на сервере
- Гарантирует, что код на сервере точно совпадает с кодом в GitHub
- Предотвращает конфликты при `git pull`
- **ВНИМАНИЕ**: Это необратимая операция!

### ❓ Что делать, если деплой завершился с ошибкой?

**Ответ**:
1. Проверьте GitHub Actions на наличие ошибки
2. Подключитесь к серверу по SSH
3. Проверьте логи:
   ```bash
   sudo journalctl -u rli-systems.service -n 100
   ```
4. Проверьте статус сервиса:
   ```bash
   sudo systemctl status rli-systems.service
   ```
5. Проверьте, выполнился ли `update.sh`:
   ```bash
   cd /var/www/apps/rlisystems_v1/python_version
   git log -1  # Последний коммит
   ```

### ❓ Как откатиться к предыдущей версии?

**Ответ**:
```bash
# Подключиться к серверу
ssh user@server

# Перейти в папку проекта
cd /var/www/apps/rlisystems_v1/python_version

# Откатиться на N коммитов назад
git reset --hard HEAD~1  # На 1 коммит назад

# Или к конкретному коммиту
git reset --hard a1b2c3d

# Перезапустить сервис
sudo systemctl restart rli-systems.service
```

### ❓ Можно ли отключить автоматический деплой?

**Ответ**:
Да, есть два способа:

1. **Временно отключить workflow:**
   - GitHub → Actions → Deploy to Production Server → Disable workflow

2. **Удалить workflow файлы:**
   ```bash
   git rm .github/workflows/deploy.yml
   git commit -m "Disable auto-deploy"
   git push
   ```

### ❓ Как деплоить вручную без GitHub Actions?

**Ответ**:
```bash
# Подключиться к серверу
ssh user@server

# Перейти в папку проекта
cd /var/www/apps/rlisystems_v1/python_version

# Выполнить update.sh
bash update.sh

# Перезапустить сервис
sudo systemctl restart rli-systems.service
```

### ❓ Где хранятся данные приложения?

**Ответ**:
- Все данные хранятся в JSON файлах
- Расположение: `~/.rlisystems_python/`
- Файлы: `tasks.json`, `settings.json`, `references.json`, `logs.json`
- Не требует базы данных

### ❓ Как узнать, какая версия кода сейчас на сервере?

**Ответ**:

1. **Через SSH**:
   ```bash
   cd /var/www/apps/rlisystems_v1/python_version
   git log -1 --oneline
   ```

2. **Через GitHub Actions**:
   - Последний успешный деплой показывает коммит

---

## 12. 🎯 Чеклист для настройки нового сервера

### 1. Установка необходимого ПО
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Python и pip
sudo apt install python3 python3-pip python3-venv -y

# Git
sudo apt install git -y

# Chrome/Chromium для Selenium
sudo apt install chromium-browser chromium-chromedriver -y

# Nginx (опционально, для reverse proxy)
sudo apt install nginx -y
```

### 2. Создание пользователя и папок
```bash
# Создание папки для production
sudo mkdir -p /var/www/apps/rlisystems_v1/python_version
sudo chown $USER:$USER /var/www/apps/rlisystems_v1/python_version

# Создание папки для development (опционально)
sudo mkdir -p /var/www/apps/rlisystems_v1/python_version-dev
sudo chown $USER:$USER /var/www/apps/rlisystems_v1/python_version-dev
```

### 3. Клонирование репозитория
```bash
# Production
cd /var/www/apps/rlisystems_v1/python_version
git clone https://github.com/your-org/rlisystems_v1.git .
git checkout main
```

### 4. Настройка Python окружения
```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 5. Настройка systemd сервиса
```bash
# Скопировать файл сервиса
sudo cp systemd/rli-systems.service /etc/systemd/system/

# Отредактировать пути (если нужно)
sudo nano /etc/systemd/system/rli-systems.service

# Перезагрузить systemd
sudo systemctl daemon-reload

# Включить автозапуск
sudo systemctl enable rli-systems.service

# Запустить сервис
sudo systemctl start rli-systems.service

# Проверить статус
sudo systemctl status rli-systems.service
```

### 6. Настройка SSH ключей для GitHub Actions
```bash
# Генерация SSH ключа
ssh-keygen -t rsa -b 4096 -C "github-actions"

# Добавление публичного ключа в authorized_keys
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

# Скопировать приватный ключ для GitHub Secrets
cat ~/.ssh/id_rsa
```

### 7. Настройка GitHub Secrets
1. Открыть репозиторий на GitHub
2. Settings → Secrets and variables → Actions
3. Добавить секреты:
   - `VDS_HOST` - IP адрес сервера
   - `VDS_USERNAME` - имя пользователя SSH
   - `VDS_SSH_KEY` - содержимое приватного ключа

### 8. Тестирование деплоя
```bash
# Сделать тестовый коммит
git add .
git commit -m "Test deploy"
git push origin main

# Проверить статус на GitHub
# GitHub → Actions → Deploy to Production Server

# Проверить работу сервера
curl http://localhost:8088/api/tasks
curl http://localhost:8088/docs  # Swagger документация
```

---

## 13. 🛡️ Безопасность

### Важные рекомендации:

1. **Не коммитьте секретные данные в Git!**
   - Добавьте `.env` в `.gitignore` (если используется)
   - Используйте переменные окружения на сервере

2. **Ограничьте SSH доступ:**
   ```bash
   # Отключить авторизацию по паролю (только ключи)
   sudo nano /etc/ssh/sshd_config
   # PasswordAuthentication no
   sudo systemctl restart sshd
   ```

3. **Настройте firewall:**
   ```bash
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 80/tcp   # HTTP
   sudo ufw allow 443/tcp  # HTTPS
   sudo ufw enable
   ```

4. **Регулярно обновляйте систему:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

5. **Используйте HTTPS:**
   - Настройте Nginx с SSL сертификатом
   - Используйте Let's Encrypt для бесплатных сертификатов

---

## 14. 📚 Полезные ссылки

### Документация:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [Selenium](https://selenium-python.readthedocs.io/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [systemd](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

## 15. 📞 Поддержка

Если у вас возникли вопросы или проблемы:

1. Проверьте логи: `sudo journalctl -u rli-systems.service -n 100`
2. Проверьте статус сервисов: `sudo systemctl status rli-systems.service`
3. Проверьте GitHub Actions на наличие ошибок
4. Проверьте, что все пути в systemd сервисе корректны

---

**Последнее обновление**: Январь 2025  
**Версия документа**: 2.0

---

## 🎉 Готово!

Теперь у вас есть полное понимание того, как работает система автоматического деплоя. При каждом `git push` код автоматически обновляется на сервере, обновляются зависимости, и сервис перезапускается с новой версией кода.

**Ключевые моменты:**
- ✅ Автоматический деплой через GitHub Actions
- ✅ Безопасное обновление через SSH
- ✅ Автоматическое обновление зависимостей
- ✅ Graceful restart сервиса
- ✅ Две среды: Production и Development
- ✅ Не требует базы данных - все данные в JSON файлах
