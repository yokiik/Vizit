# 🚀 Быстрая настройка GitHub Actions для автоматического деплоя

## Шаги настройки

### 1. Добавьте SSH ключ на сервер

На вашем локальном компьютере или на сервере:

```bash
# Генерация SSH ключа (если еще нет)
ssh-keygen -t rsa -b 4096 -C "github-actions"

# Просмотр публичного ключа
cat ~/.ssh/id_rsa.pub

# Скопируйте этот ключ и добавьте на сервер:
ssh-copy-id user@your-server-ip
# Или вручную:
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
```

### 2. Добавьте секреты в GitHub

1. Откройте ваш репозиторий на GitHub
2. Перейдите: **Settings** → **Secrets and variables** → **Actions**
3. Нажмите **New repository secret**

Добавьте три секрета:

| Название | Значение | Как получить |
|----------|----------|--------------|
| `VDS_HOST` | IP адрес вашего сервера | Например: `123.45.67.89` |
| `VDS_USERNAME` | Имя пользователя SSH | Обычно `root` или `ubuntu` |
| `VDS_SSH_KEY` | Приватный SSH ключ | `cat ~/.ssh/id_rsa` (на вашем компьютере) |

**Важно:** 
- Для `VDS_SSH_KEY` скопируйте ВЕСЬ файл, включая строки `-----BEGIN` и `-----END`
- Это приватный ключ, храните его в секрете!

### 3. Подготовьте сервер

На сервере выполните:

```bash
# Создайте директорию для проекта
sudo mkdir -p /var/www/apps/rlisystems_v1/python_version
sudo chown $USER:$USER /var/www/apps/rlisystems_v1/python_version

# Клонируйте репозиторий
cd /var/www/apps/rlisystems_v1/python_version
git clone https://github.com/your-username/rlisystems_v1.git .

# Установите systemd сервис
sudo cp systemd/rli-systems.service /etc/systemd/system/
sudo nano /etc/systemd/system/rli-systems.service  # Проверьте пути
sudo systemctl daemon-reload
sudo systemctl enable rli-systems.service

# Сделайте скрипт исполняемым
chmod +x update.sh
```

### 4. Настройте права доступа для sudo

Чтобы GitHub Actions мог перезапускать сервис без пароля:

```bash
sudo visudo

# Добавьте строку (замените username на вашего пользователя):
username ALL=(ALL) NOPASSWD: /bin/systemctl restart rli-systems.service
username ALL=(ALL) NOPASSWD: /bin/systemctl restart rli-systems-dev.service
```

Или для пользователя www-data (если сервис запускается от его имени):

```bash
www-data ALL=(ALL) NOPASSWD: /bin/systemctl restart rli-systems.service
```

### 5. Проверьте настройку

После настройки секретов:

1. Сделайте тестовый коммит:
   ```bash
   git add .
   git commit -m "Test GitHub Actions deploy"
   git push origin main
   ```

2. Проверьте GitHub Actions:
   - Откройте вкладку **Actions** в вашем репозитории
   - Убедитесь, что workflow запустился
   - Проверьте логи выполнения

3. Проверьте сервер:
   ```bash
   ssh user@your-server
   cd /var/www/apps/rlisystems_v1/python_version
   git log -1  # Должен быть последний коммит
   sudo systemctl status rli-systems.service
   ```

### 6. Проверьте работу приложения

```bash
# Проверьте, что сервис запущен
curl http://localhost:8088/api/tasks

# Или через браузер
# http://your-server-ip:8088
# http://your-server-ip:8088/docs  # Swagger документация
```

## Troubleshooting

### Ошибка SSH подключения

**Симптом:** `Permission denied (publickey)`

**Решение:**
1. Убедитесь, что публичный ключ добавлен на сервер в `~/.ssh/authorized_keys`
2. Проверьте права доступа:
   ```bash
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```
3. Проверьте, что приватный ключ в GitHub Secrets правильный (со всеми строками)

### Ошибка при выполнении update.sh

**Симптом:** `bash: update.sh: Permission denied`

**Решение:**
```bash
chmod +x /var/www/apps/rlisystems_v1/python_version/update.sh
```

### Ошибка перезапуска сервиса

**Симптом:** `sudo: no tty present and no askpass program specified`

**Решение:**
1. Настройте sudo без пароля (шаг 4 выше)
2. Убедитесь, что путь к systemctl правильный: `/bin/systemctl` или `/usr/bin/systemctl`

### Сервис не запускается

**Решение:**
```bash
# Проверьте логи
sudo journalctl -u rli-systems.service -n 50

# Проверьте конфигурацию
sudo systemctl status rli-systems.service

# Убедитесь, что пути в service файле правильные
cat /etc/systemd/system/rli-systems.service
```

## Готово!

После выполнения всех шагов, при каждом `git push` в ветку `main` или `master` код автоматически обновится на сервере.

Для проверки посмотрите вкладку **Actions** в вашем GitHub репозитории - там будут видны все деплои и их статусы.

