# ⚡ Быстрое развертывание на сервере

## 📋 Что потребуется

1. Сервер с Ubuntu 20.04+ или Debian 11+
2. Доступ по SSH
3. Минимум 2GB RAM, 4GB рекомендуется

## 🚀 Быстрый старт (5 минут)

### Шаг 1: Подключитесь к серверу

```bash
ssh user@your-server-ip
```

### Шаг 2: Установите необходимые пакеты

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git nginx
```

### Шаг 3: Клонируйте проект

```bash
cd /var/www
sudo mkdir -p apps
sudo chown $USER:$USER apps
cd apps
git clone https://github.com/ваш-username/rlisystems_v1.git
cd rlisystems_v1/python_version
```

### Шаг 4: Настройте приложение

```bash
# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### Шаг 5: Настройте Nginx

```bash
# Копируем конфигурацию
sudo cp nginx/rli-systems.conf /etc/nginx/sites-available/rli-systems

# Редактируем для вашего домена/IP
sudo nano /etc/nginx/sites-available/rli-systems

# Активируем и проверяем
sudo ln -s /etc/nginx/sites-available/rli-systems /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

В файле `/etc/nginx/sites-available/rli-systems` измените:

```nginx
server_name ваш-домен.com или IP_адрес;
```

### Шаг 6: Запустите через Gunicorn вручную (для теста)

```bash
source venv/bin/activate
gunicorn --config gunicorn_config.py wsgi:application
```

Проверьте работу: откройте в браузере `http://ваш-ip-адрес`

### Шаг 7: Настройте автозапуск

```bash
# Копируем service файл
sudo cp systemd/rli-systems.service /etc/systemd/system/

# Редактируем пути в файле, если они отличаются
sudo nano /etc/systemd/system/rli-systems.service

# Активируем и запускаем
sudo systemctl daemon-reload
sudo systemctl enable rli-systems.service
sudo systemctl start rli-systems.service

# Проверяем статус
sudo systemctl status rli-systems.service
```

### Шаг 8: Настройте автообновление

```bash
# Делаем скрипт исполняемым
chmod +x deploy.sh

# Настраиваем cron для ежедневного обновления
crontab -e
```

Добавьте строку (обновление каждый день в 3:00):

```
0 3 * * * /var/www/apps/rlisystems_v1/python_version/deploy.sh >> /var/log/rli-auto-update.log 2>&1
```

## ✅ Готово!

Теперь ваше приложение доступно по адресу: `http://ваш-ip-адрес`

## 🛠 Полезные команды

```bash
# Проверить статус
sudo systemctl status rli-systems.service

# Перезапустить
sudo systemctl restart rli-systems.service

# Посмотреть логи
sudo journalctl -u rli-systems.service -f

# Ручное обновление
cd /var/www/apps/rlisystems_v1/python_version
./deploy.sh
```

## 🔧 Настройка для нескольких приложений

### 1. Создайте вторую директорию

```bash
cd /var/www/apps
mkdir second-app
cd second-app

# Здесь разместите ваш второй проект
# Используйте порт 8089 для второго приложения
```

### 2. Создайте конфигурацию Nginx

```bash
sudo nano /etc/nginx/sites-available/second-app
```

```nginx
server {
    listen 80;
    server_name второй-домен.com или IP_адрес;

    location / {
        proxy_pass http://127.0.0.1:8089;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Активируем
sudo ln -s /etc/nginx/sites-available/second-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Создайте второй Systemd сервис

```bash
sudo cp systemd/rli-systems.service /etc/systemd/system/second-app.service
sudo nano /etc/systemd/system/second-app.service
```

Измените:
- `Description` на "Second Application"
- `PORT=8089`
- `WorkingDirectory` и пути на пути второго приложения
- Порт в `ExecStart` на 8089

```bash
sudo systemctl daemon-reload
sudo systemctl enable second-app.service
sudo systemctl start second-app.service
```

## 🌍 Доступ из интернета

### Откройте порты в firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw enable
```

### Проверьте, что приложение работает

Откройте в браузере: `http://ваш-ip-адрес`

## 📊 Мониторинг

### Проверка портов

```bash
sudo netstat -tlnp | grep -E '8088|8089'
```

### Проверка логов Nginx

```bash
sudo tail -f /var/log/nginx/rli-systems_access.log
sudo tail -f /var/log/nginx/rli-systems_error.log
```

## 🔐 SSL/HTTPS (опционально)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d ваш-домен.com
```

Сертификат будет автоматически продлеваться.

---

**🎉 Поздравляем!** Ваше приложение развернуто и готово к работе!

