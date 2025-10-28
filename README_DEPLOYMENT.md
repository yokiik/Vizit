# 📖 Руководство по развертыванию RLI Systems

## 📚 Документация

Выберите нужный документ:

1. **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** - ⚡ Быстрый старт (5 минут)
   - Для новичков
   - Минимальная настройка
   - Автоматический запуск

2. **[DEPLOYMENT.md](DEPLOYMENT.md)** - 🚀 Полное руководство
   - Детальная настройка
   - Многосайтовая конфигурация
   - Мониторинг и бэкапы
   - SSL/HTTPS
   - Устранение неполадок

## 🎯 Что вы получите

После развертывания у вас будет:

✅ **Веб-сервер**, доступный из интернета  
✅ **Автоматическое обновление** с GitHub  
✅ **Nginx** как reverse proxy  
✅ **Systemd** для автозапуска  
✅ **Возможность** запускать несколько приложений на одном сервере  
✅ **Резервное копирование** данных  

## 🏗 Архитектура развертывания

```
Интернет → Nginx (порт 80) → Gunicorn (порт 8088) → Flask приложение
                                   ↕
                            JSON хранилище (~/.rlisystems_python)
```

## 📦 Структура файлов развертывания

```
python_version/
├── deploy.sh                    # Скрипт автообновления с GitHub
├── gunicorn_config.py           # Конфигурация Gunicorn
├── wsgi.py                      # WSGI точка входа
├── systemd/
│   └── rli-systems.service      # Systemd сервис
├── nginx/
│   └── rli-systems.conf         # Конфигурация Nginx
└── backup/                      # Директория для бэкапов (создается автоматически)
```

## 🔄 Процесс развертывания

### 1. Подготовка сервера

```bash
# Установка зависимостей
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git nginx
```

### 2. Установка приложения

```bash
# Клонирование
cd /var/www/apps
git clone https://github.com/ваш-username/rlisystems_v1.git
cd rlisystems_v1/python_version

# Настройка
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Настройка Nginx

```bash
# Копирование конфигурации
sudo cp nginx/rli-systems.conf /etc/nginx/sites-available/rli-systems

# Редактирование
sudo nano /etc/nginx/sites-available/rli-systems

# Активирование
sudo ln -s /etc/nginx/sites-available/rli-systems /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Настройка Systemd

```bash
# Копирование service файла
sudo cp systemd/rli-systems.service /etc/systemd/system/

# Редактирование (при необходимости)
sudo nano /etc/systemd/system/rli-systems.service

# Запуск
sudo systemctl daemon-reload
sudo systemctl enable rli-systems.service
sudo systemctl start rli-systems.service
```

### 5. Настройка автообновления

```bash
# Делаем скрипт исполняемым
chmod +x deploy.sh

# Настраиваем cron
crontab -e
```

Добавьте:
```
0 3 * * * /var/www/apps/rlisystems_v1/python_version/deploy.sh >> /var/log/rli-auto-update.log 2>&1
```

## 🎛 Управление приложением

### Основные команды

```bash
# Проверка статуса
sudo systemctl status rli-systems.service

# Запуск
sudo systemctl start rli-systems.service

# Остановка
sudo systemctl stop rli-systems.service

# Перезапуск
sudo systemctl restart rli-systems.service

# Логи
sudo journalctl -u rli-systems.service -f

# Ручное обновление
cd /var/www/apps/rlisystems_v1/python_version
./deploy.sh
```

## 🔧 Настройка для нескольких приложений

### Вариант 1: Разные порты

Приложение 1 → порт 8088  
Приложение 2 → порт 8089

Конфигурация Nginx создает разные поддомены или использует разные порты.

### Вариант 2: Разные поддомены

```
https://app1.ваш-домен.com → порт 8088
https://app2.ваш-домен.com → порт 8089
```

### Вариант 3: Разные пути

```
https://ваш-домен.com/app1/ → порт 8088
https://ваш-домен.com/app2/ → порт 8089
```

Конфигурация в `nginx/rli-systems.conf` показывает примеры.

## 📊 Мониторинг

### Логи приложения

```bash
# Последние 100 строк
sudo journalctl -u rli-systems.service -n 100

# В реальном времени
sudo journalctl -u rli-systems.service -f

# Ошибки
sudo journalctl -u rli-systems.service -p err
```

### Логи Nginx

```bash
# Доступы
sudo tail -f /var/log/nginx/rli-systems_access.log

# Ошибки
sudo tail -f /var/log/nginx/rli-systems_error.log
```

### Логи автообновления

```bash
tail -f /var/log/rli-auto-update.log
```

### Мониторинг ресурсов

```bash
# CPU и память
htop

# Запущенные процессы
ps aux | grep gunicorn

# Открытые порты
sudo netstat -tlnp | grep python
```

## 🔐 Безопасность

### 1. Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. SSL/HTTPS

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d ваш-домен.com
```

### 3. Ограничение доступа

В `/etc/nginx/sites-available/rli-systems` можно добавить:

```nginx
# Разрешить доступ только с определенных IP
location / {
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;
    
    proxy_pass http://127.0.0.1:8088;
    # ... остальные настройки
}
```

## 💾 Резервное копирование

### Автоматическое (через cron)

```bash
# Создаем скрипт
nano /var/www/apps/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/rli-systems"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Бэкап данных
tar -czf $BACKUP_DIR/data_$DATE.tar.gz ~/.rlisystems_python/

# Бэкап кода
tar -czf $BACKUP_DIR/code_$DATE.tar.gz /var/www/apps/

# Удаляем старые (старше 7 дней)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
chmod +x /var/www/apps/backup.sh
crontab -e
```

Добавьте:
```
0 2 * * * /var/www/apps/backup.sh
```

### Ручное восстановление

```bash
# Восстановление данных
tar -xzf /var/backups/rli-systems/data_YYYYMMDD_HHMMSS.tar.gz -C ~/

# Восстановление кода
tar -xzf /var/backups/rli-systems/code_YYYYMMDD_HHMMSS.tar.gz -C /
```

## 🚨 Устранение неполадок

### Приложение не запускается

```bash
# Проверка логов
sudo journalctl -u rli-systems.service -n 50

# Проверка порта
sudo netstat -tlnp | grep 8088

# Проверка зависимостей
cd /var/www/apps/rlisystems_v1/python_version
source venv/bin/activate
python -c "import flask, selenium"
```

### Nginx не может подключиться

```bash
# Проверка, что приложение запущено
ps aux | grep gunicorn

# Проверка конфигурации Nginx
sudo nginx -t

# Перезагрузка Nginx
sudo systemctl reload nginx
```

### Ошибки при автообновлении

```bash
# Проверка логов
tail -50 /var/log/rli-auto-update.log

# Ручной запуск скрипта
cd /var/www/apps/rlisystems_v1/python_version
./deploy.sh
```

## 📈 Оптимизация производительности

### Настройка количества workers

В `gunicorn_config.py`:

```python
# Для слабых серверов (2 ядра)
workers = 2

# Для средних (4 ядра)
workers = 4

# Для мощных (8+ ядер)
workers = 8
```

### Настройка Nginx

В `/etc/nginx/nginx.conf`:

```nginx
# Вне блока server
gzip on;
gzip_vary on;
gzip_min_length 10240;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

## 📞 Поддержка

Если возникли проблемы:

1. Проверьте логи: `sudo journalctl -u rli-systems.service`
2. Проверьте Nginx: `sudo nginx -t`
3. Проверьте порты: `sudo netstat -tlnp`
4. Проверьте firewall: `sudo ufw status`

## 🎓 Дополнительная информация

- [Flask документация](https://flask.palletsprojects.com/)
- [Gunicorn документация](https://docs.gunicorn.org/)
- [Nginx документация](https://nginx.org/en/docs/)
- [Systemd документация](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

**Приятного использования! 🚀**

