# 🚀 Развертывание на сервере

## Содержание

1. [Подготовка сервера](#1-подготовка-сервера)
2. [Установка зависимостей](#2-установка-зависимостей)
3. [Настройка Python приложения](#3-настройка-python-приложения)
4. [Настройка Nginx как reverse proxy](#4-настройка-nginx-как-reverse-proxy)
5. [Настройка автоматического обновления с GitHub](#5-настройка-автоматического-обновления-с-github)
6. [Настройка Systemd Service](#6-настройка-systemd-service)
7. [Многосайтовая конфигурация](#7-многосайтовая-конфигурация)

## 1. Подготовка сервера

### Требования к серверу

- **ОС:** Ubuntu 20.04+ / Debian 11+
- **Python:** 3.9+
- **RAM:** минимум 4GB (рекомендуется 8GB)
- **Диск:** 20GB свободного места
- **Open порты:** 80, 443, 22

### Обновление системы

```bash
sudo apt update && sudo apt upgrade -y
```

## 2. Установка зависимостей

### Установка Python и базовых инструментов

```bash
sudo apt install -y python3 python3-pip python3-venv git nginx supervisor
```

### Установка Chrome для автоматизации

```bash
# Установка Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt install -f -y
```

## 3. Настройка Python приложения

### Клонирование репозитория

```bash
# Создаем директорию для проектов
sudo mkdir -p /var/www/apps
sudo chown $USER:$USER /var/www/apps

# Клонируем проект
cd /var/www/apps
git clone https://github.com/ваш-username/rlisystems_v1.git
cd rlisystems_v1/python_version
```

### Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn  # Добавляем production WSGI сервер
```

### Настройка переменных окружения

```bash
# Создаем .env файл
cat > .env << EOF
PORT=8088
PYTHONUNBUFFERED=1
EOF
```

## 4. Настройка Nginx как reverse proxy

### Создаем конфигурацию для первого приложения

```bash
sudo nano /etc/nginx/sites-available/rli-systems
```

Вставьте следующую конфигурацию:

```nginx
server {
    listen 80;
    server_name ваш-домен-1.com или IP_адрес;

    location / {
        proxy_pass http://127.0.0.1:8088;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Логи
    access_log /var/log/nginx/rli-systems_access.log;
    error_log /var/log/nginx/rli-systems_error.log;
}
```

Активируем конфигурацию:

```bash
sudo ln -s /etc/nginx/sites-available/rli-systems /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 5. Настройка автоматического обновления с GitHub

### Создаем скрипт автообновления

```bash
nano /var/www/apps/rlisystems_v1/python_version/deploy.sh
```

```bash
#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔄 Начинаем обновление проекта...${NC}"

# Переходим в директорию проекта
cd /var/www/apps/rlisystems_v1/python_version || exit 1

# Сохраняем текущую версию
CURRENT_VERSION=$(git rev-parse HEAD)

# Получаем последние изменения
echo -e "${YELLOW}📥 Получаем последние изменения из GitHub...${NC}"
git fetch origin

# Проверяем, есть ли новые изменения
LATEST_VERSION=$(git rev-parse origin/master)

if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
    echo -e "${GREEN}✅ У вас уже последняя версия!${NC}"
    exit 0
fi

echo -e "${YELLOW}📦 Обновляем код...${NC}"
git pull origin master

# Активируем виртуальное окружение
source venv/bin/activate

# Обновляем зависимости
echo -e "${YELLOW}📦 Обновляем зависимости...${NC}"
pip install -r requirements.txt

# Перезапускаем приложение
echo -e "${YELLOW}🔄 Перезапускаем приложение...${NC}"
sudo systemctl restart rli-systems.service

echo -e "${GREEN}✅ Обновление завершено!${NC}"
echo -e "${GREEN}📊 Предыдущая версия: ${CURRENT_VERSION}${NC}"
echo -e "${GREEN}📊 Текущая версия: ${LATEST_VERSION}${NC}"
```

Делаем скрипт исполняемым:

```bash
chmod +x /var/www/apps/rlisystems_v1/python_version/deploy.sh
```

### Настраиваем cron для автоматического обновления

```bash
crontab -e
```

Добавьте строку для ежедневного обновления в 3:00 ночи:

```
0 3 * * * /var/www/apps/rlisystems_v1/python_version/deploy.sh >> /var/log/rli-auto-update.log 2>&1
```

## 6. Настройка Systemd Service

### Создаем service файл

```bash
sudo nano /etc/systemd/system/rli-systems.service
```

Вставьте следующую конфигурацию:

```ini
[Unit]
Description=RLI Systems Python Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/apps/rlisystems_v1/python_version
Environment="PATH=/var/www/apps/rlisystems_v1/python_version/venv/bin"
Environment="PORT=8088"
ExecStart=/var/www/apps/rlisystems_v1/python_version/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8088 --timeout 300 --log-level info main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активируем и запускаем сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable rli-systems.service
sudo systemctl start rli-systems.service
sudo systemctl status rli-systems.service
```

## 7. Многосайтовая конфигурация

### Создание второго приложения

Предположим, у вас есть второй проект. Создаем структуру:

```bash
cd /var/www/apps
mkdir -p second-app
cd second-app
# Здесь разместите ваш второй проект
```

### Настройка второго приложения на порту 8089

Создаем Nginx конфигурацию:

```bash
sudo nano /etc/nginx/sites-available/second-app
```

```nginx
server {
    listen 80;
    server_name ваш-домен-2.com;

    location / {
        proxy_pass http://127.0.0.1:8089;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    access_log /var/log/nginx/second-app_access.log;
    error_log /var/log/nginx/second-app_error.log;
}
```

Активируем:

```bash
sudo ln -s /etc/nginx/sites-available/second-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Создаем systemd сервис для второго приложения

```bash
sudo nano /etc/systemd/system/second-app.service
```

```ini
[Unit]
Description=Second Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/apps/second-app
Environment="PATH=/var/www/apps/second-app/venv/bin"
Environment="PORT=8089"
ExecStart=/var/www/apps/second-app/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8089 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## Управление приложением

### Команды для управления

```bash
# Посмотреть статус
sudo systemctl status rli-systems.service

# Перезапустить
sudo systemctl restart rli-systems.service

# Остановить
sudo systemctl stop rli-systems.service

# Запустить
sudo systemctl start rli-systems.service

# Посмотреть логи
sudo journalctl -u rli-systems.service -f
```

### Ручное обновление с GitHub

```bash
cd /var/www/apps/rlisystems_v1/python_version
./deploy.sh
```

## Настройка SSL (опционально)

### Установка Certbot

```bash
sudo apt install certbot python3-certbot-nginx
```

### Получение SSL сертификата

```bash
sudo certbot --nginx -d ваш-домен.com
```

Сертификат будет автоматически обновляться.

## Мониторинг

### Проверка портов

```bash
sudo netstat -tlnp | grep python
```

### Проверка логов

```bash
# Логи приложения
sudo journalctl -u rli-systems.service -f

# Логи Nginx
sudo tail -f /var/log/nginx/rli-systems_error.log
sudo tail -f /var/log/nginx/rli-systems_access.log

# Логи автообновления
tail -f /var/log/rli-auto-update.log
```

## Безопасность

### Настройка firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Смена владельца файлов

```bash
sudo chown -R www-data:www-data /var/www/apps
```

## Резервное копирование

### Создаем скрипт бэкапа

```bash
nano /var/www/apps/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/rli-systems"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Бэкап данных приложения
tar -czf $BACKUP_DIR/data_$DATE.tar.gz ~/.rlisystems_python/

# Бэкап кода
tar -czf $BACKUP_DIR/code_$DATE.tar.gz /var/www/apps/

# Удаляем старые бэкапы (старше 7 дней)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

Добавляем в cron:

```bash
0 2 * * * /var/www/apps/backup.sh
```

## Устранение неполадок

### Проблема: Приложение не запускается

```bash
# Проверяем логи
sudo journalctl -u rli-systems.service -n 50

# Проверяем синтаксис service файла
systemd-analyze verify /etc/systemd/system/rli-systems.service

# Проверяем зависимости
cd /var/www/apps/rlisystems_v1/python_version
source venv/bin/activate
python -c "import flask, selenium"
```

### Проблема: Nginx не может подключиться к приложению

```bash
# Проверяем, что приложение запущено
ps aux | grep gunicorn

# Проверяем порт
netstat -tlnp | grep 8088
```

### Проблема: Ошибки в Nginx

```bash
# Проверяем конфигурацию
sudo nginx -t

# Перезагружаем Nginx
sudo systemctl reload nginx
```

## Производительность

### Настройка количества worker процессов

В файле `/etc/systemd/system/rli-systems.service` измените:

```ini
# Для слабых серверов (2 ядра)
ExecStart=... --workers 2 ...

# Для средних серверов (4 ядра)
ExecStart=... --workers 4 ...

# Для мощных серверов (8+ ядер)
ExecStart=... --workers 8 ...
```

### Оптимизация Nginx

Добавьте в `/etc/nginx/nginx.conf`:

```nginx
# За пределами блока server
gzip on;
gzip_vary on;
gzip_min_length 10240;
gzip_proxied expired no-cache no-store private auth;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
```

## Подключение с других компьютеров

После развертывания, другие люди смогут подключиться по IP адресу или домену:

```
http://ВАШ_IP_АДРЕС/
или
http://ваш-домен.com/
```

Если используете разные порты:

```
http://ВАШ_IP_АДРЕС/          # Первое приложение (порт 8088)
http://ВАШ_IP_АДРЕС/          # Второе приложение (порт 8089)
```

Для разделения по поддоменам используйте разные `server_name` в конфигурации Nginx.

---

✅ **Готово!** Ваше приложение развернуто и доступно в интернете.

