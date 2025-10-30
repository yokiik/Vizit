# ✅ Чеклист настройки автоматического деплоя

Отмечайте галочками выполненные шаги:

## Шаг 1: GitHub Secrets

- [ ] Открыл Settings → Secrets and variables → Actions в репозитории
- [ ] Добавил секрет `VDS_HOST` (IP адрес сервера)
- [ ] Добавил секрет `VDS_USERNAME` (SSH пользователь)
- [ ] Добавил секрет `VDS_SSH_KEY` (приватный SSH ключ)
- [ ] Проверил, что ключ скопирован полностью (со всеми строками)

## Шаг 2: SSH ключи

- [ ] Создал SSH ключ (если еще нет): `ssh-keygen -t rsa -b 4096`
- [ ] Посмотрел публичный ключ: `cat ~/.ssh/id_rsa.pub`
- [ ] Скопировал публичный ключ на сервер
- [ ] Проверил добавление: `cat ~/.ssh/authorized_keys` на сервере
- [ ] Проверил права: `chmod 600 ~/.ssh/authorized_keys`

## Шаг 3: Подготовка сервера

- [ ] Подключился к серверу по SSH
- [ ] Создал директорию: `/var/www/apps/rlisystems_v1/python_version`
- [ ] Клонировал репозиторий в эту директорию
- [ ] Проверил, что файлы на месте: `ls -la`

## Шаг 4: Systemd сервис

- [ ] Скопировал сервис: `sudo cp systemd/rli-systems.service /etc/systemd/system/`
- [ ] Проверил содержимое: `cat /etc/systemd/system/rli-systems.service`
- [ ] Обновил демон: `sudo systemctl daemon-reload`
- [ ] Включил автозапуск: `sudo systemctl enable rli-systems.service`
- [ ] Запустил сервис: `sudo systemctl start rli-systems.service`
- [ ] Проверил статус: `sudo systemctl status rli-systems.service`

## Шаг 5: Права sudo

- [ ] Открыл: `sudo visudo`
- [ ] Добавил строку для перезапуска сервиса без пароля
- [ ] Сохранил файл
- [ ] Проверил, что команда работает: `sudo systemctl restart rli-systems.service`

## Шаг 6: Скрипт update.sh

- [ ] Убедился, что файл `update.sh` существует на сервере
- [ ] Сделал исполняемым: `chmod +x update.sh`
- [ ] Проверил содержимое: `cat update.sh`

## Шаг 7: Первый деплой

- [ ] Сделал тестовый коммит локально: `git add . && git commit -m "Test"`
- [ ] Отправил в GitHub: `git push origin main`
- [ ] Открыл вкладку Actions в GitHub
- [ ] Проверил, что workflow запустился
- [ ] Дождался завершения деплоя (зеленая галочка)
- [ ] Проверил логи в GitHub Actions

## Шаг 8: Проверка на сервере

- [ ] Подключился к серверу
- [ ] Проверил последний коммит: `git log -1`
- [ ] Проверил статус сервиса: `sudo systemctl status rli-systems.service`
- [ ] Проверил работу API: `curl http://localhost:8088/api/tasks`
- [ ] Проверил Swagger: открыл в браузере `http://SERVER_IP:8088/docs`

## Шаг 9: Проверка работы приложения

- [ ] Открыл Swagger UI: http://SERVER_IP:8088/docs
- [ ] Протестировал GET /api/tasks
- [ ] Протестировал GET /api/settings
- [ ] Протестировал GET /api/references
- [ ] Проверил логи: `sudo journalctl -u rli-systems.service -n 50`

## Готово! 🎉

Все шаги выполнены. Автоматический деплой настроен!

---

## Если что-то пошло не так

### Проблема: GitHub Actions показывает ошибку

**Проверьте:**
1. Все ли секреты добавлены в GitHub Secrets
2. Правильный ли SSH ключ
3. Подключается ли SSH с вашего компьютера к серверу: `ssh user@server`
4. Логи выполнения в GitHub Actions

### Проблема: Сервис не запускается

**Выполните:**
```bash
# Проверьте логи
sudo journalctl -u rli-systems.service -f

# Проверьте конфигурацию
sudo systemctl status rli-systems.service

# Проверьте, что зависимости установлены
cd /var/www/apps/rlisystems_v1/python_version
source venv/bin/activate
pip list
```

### Проблема: update.sh не работает

**Выполните:**
```bash
# Запустите скрипт вручную
cd /var/www/apps/rlisystems_v1/python_version
bash update.sh

# Посмотрите ошибки
```

### Проблема: Порт 8088 недоступен

**Выполните:**
```bash
# Проверьте, что порт открыт
sudo netstat -tlnp | grep 8088

# Проверьте firewall
sudo ufw status
# Если нужно, откройте порт:
sudo ufw allow 8088/tcp
```

---

## Полезные ссылки

- GitHub Actions: https://github.com/YOUR_USERNAME/YOUR_REPO/actions
- Swagger UI: http://SERVER_IP:8088/docs
- Логи сервиса: `sudo journalctl -u rli-systems.service -f`

## Команды для ежедневного использования

```bash
# Посмотреть статус
sudo systemctl status rli-systems.service

# Посмотреть последние логи
sudo journalctl -u rli-systems.service -n 100

# Перезапустить сервис
sudo systemctl restart rli-systems.service

# Остановить сервис
sudo systemctl stop rli-systems.service

# Запустить сервис
sudo systemctl start rli-systems.service
```

