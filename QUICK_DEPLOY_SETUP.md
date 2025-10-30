# 🚀 Быстрая настройка автоматического деплоя

## Что уже готово

✅ GitHub Actions workflows (.github/workflows/)
✅ Скрипт обновления (update.sh)
✅ Systemd сервисы (systemd/)
✅ Исправлена кодировка для Windows

## Что нужно сделать

### 1️⃣ Настроить GitHub Secrets

Откройте ваш репозиторий на GitHub:
1. **Settings** → **Secrets and variables** → **Actions**
2. Нажмите **New repository secret**

Добавьте 3 секрета:

| Название | Значение | Описание |
|----------|----------|----------|
| `VDS_HOST` | IP вашего сервера | Например: `123.45.67.89` |
| `VDS_USERNAME` | SSH пользователь | Обычно `root` или `ubuntu` |
| `VDS_SSH_KEY` | Приватный SSH ключ | См. ниже |

#### Как получить приватный SSH ключ:

```powershell
# В Windows PowerShell
cat C:\Users\yokai\.ssh\id_rsa

# Если нет ключа, создайте:
ssh-keygen -t rsa -b 4096 -C "github-actions"
```

**⚠️ ВАЖНО:** Скопируйте ВСЁ содержимое, включая строки:
```
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

#### Добавьте публичный ключ на сервер:

```powershell
# Покажите публичный ключ
cat C:\Users\yokai\.ssh\id_rsa.pub

# Скопируйте вывод и на сервере выполните:
ssh user@your-server
echo "вставьте_публичный_ключ" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 2️⃣ Подготовить сервер

Подключитесь к вашему VDS серверу и выполните:

```bash
# Создайте директорию
sudo mkdir -p /var/www/apps/rlisystems_v1/python_version
sudo chown $USER:$USER /var/www/apps/rlisystems_v1/python_version

# Клонируйте репозиторий
cd /var/www/apps/rlisystems_v1/python_version
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git .

# Установите systemd сервис
sudo cp systemd/rli-systems.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rli-systems.service
sudo systemctl start rli-systems.service

# Убедитесь, что скрипт исполняемый
chmod +x update.sh

# Проверьте работу
sudo systemctl status rli-systems.service
```

### 3️⃣ Настроить sudo без пароля

Чтобы GitHub Actions мог перезапускать сервис:

```bash
# Откройте visudo
sudo visudo

# Добавьте в конец файла (замените YOUR_USERNAME):
YOUR_USERNAME ALL=(ALL) NOPASSWD: /bin/systemctl restart rli-systems.service
YOUR_USERNAME ALL=(ALL) NOPASSWD: /bin/systemctl restart rli-systems-dev.service
```

Сохраните (Ctrl+O, Enter, Ctrl+X в nano)

### 4️⃣ Проверить работу

Сделайте тестовый коммит:

```powershell
# В вашей локальной директории
git add .
git commit -m "Setup GitHub Actions auto-deploy"
git push origin main
```

Затем:
1. Откройте вкладку **Actions** в GitHub
2. Посмотрите, что workflow запустился
3. Проверьте логи выполнения

### 5️⃣ Проверить на сервере

```bash
ssh user@your-server

# Проверьте, что код обновился
cd /var/www/apps/rlisystems_v1/python_version
git log -1  # Должен быть ваш коммит

# Проверьте, что сервис работает
sudo systemctl status rli-systems.service

# Проверьте API
curl http://localhost:8088/api/tasks
```

## Как это работает

```
┌─────────────────┐
│  git push main  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  GitHub Actions триггер     │
│  .github/workflows/deploy.yml│
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  SSH подключение к серверу  │
│  Использует:                │
│  - VDS_HOST                 │
│  - VDS_USERNAME             │
│  - VDS_SSH_KEY              │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Выполняется на сервере:    │
│  1. cd /var/www/apps/...    │
│  2. bash update.sh          │
│  3. systemctl restart ...   │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  ✅ Деплой завершен!        │
└─────────────────────────────┘
```

## Файлы проекта

| Файл | Описание |
|------|----------|
| `.github/workflows/deploy.yml` | Production деплой (ветка main) |
| `.github/workflows/deploy-dev.yml` | Development деплой (ветка dev) |
| `update.sh` | Скрипт обновления на сервере |
| `systemd/rli-systems.service` | Systemd сервис для production |
| `systemd/rli-systems-dev.service` | Systemd сервис для development |

## Troubleshooting

### Ошибка: Permission denied (publickey)

**Решение:**
```bash
# На сервере проверьте права
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# Проверьте, что публичный ключ добавлен
cat ~/.ssh/authorized_keys
```

### Ошибка: sudo: no tty present

**Решение:** Настройте sudo без пароля (шаг 3 выше)

### Ошибка: Update script failed

**Решение:**
```bash
# Проверьте логи
sudo journalctl -u rli-systems.service -n 50

# Проверьте, что скрипт исполняемый
ls -la /var/www/apps/rlisystems_v1/python_version/update.sh
```

### Сервис не запускается

**Решение:**
```bash
# Проверьте конфигурацию
sudo systemctl status rli-systems.service

# Проверьте логи
sudo journalctl -u rli-systems.service -f

# Убедитесь, что все зависимости установлены
cd /var/www/apps/rlisystems_v1/python_version
source venv/bin/activate
pip list
```

## Готово! 🎉

Теперь при каждом `git push` в ветку `main` код автоматически деплоится на сервер.

**Swagger UI будет доступен на:** http://your-server-ip:8088/docs

## Полезные команды

```bash
# Посмотреть логи GitHub Actions
# GitHub → Actions → последний workflow

# Посмотреть логи сервиса
sudo journalctl -u rli-systems.service -f

# Перезапустить сервис вручную
sudo systemctl restart rli-systems.service

# Проверить статус
sudo systemctl status rli-systems.service

# Остановить сервис
sudo systemctl stop rli-systems.service

# Посмотреть какие порты слушает приложение
sudo netstat -tlnp | grep 8088
```

