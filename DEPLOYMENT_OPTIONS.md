# 🚀 Варианты деплоя без SSH ключа

Есть несколько способов настроить автоматический деплой:

## Вариант 1: GitHub Actions + Password Authentication ✅

Вместо SSH ключа можно использовать пароль (не самый безопасный, но работает):

### 1. Настройте GitHub Actions

Измените `.github/workflows/deploy.yml`:

```yaml
- name: Deploy to server via SSH
  uses: appleboy/ssh-action@master
  with:
    host: ${{ secrets.VDS_HOST }}
    username: ${{ secrets.VDS_USERNAME }}
    password: ${{ secrets.VDS_PASSWORD }}  # Вместо key
    script: |
      cd /var/www/apps/rlisystems_v1/python_version
      bash update.sh
      sudo systemctl restart rli-systems.service
```

### 2. Добавьте Secrets

В GitHub Secrets добавьте:
- `VDS_HOST` - IP сервера
- `VDS_USERNAME` - пользователь
- `VDS_PASSWORD` - пароль пользователя

⚠️ **Небезопасно:** пароль хранится в открытом виде в GitHub Secrets.

---

## Вариант 2: GitHub Actions + GitHub Deploy Key 🔐

Более безопасный способ без SSH ключа на вашем компьютере:

### 1. Создайте Deploy Key на сервере

На вашем VDS сервере:

```bash
# Создайте SSH ключ специально для GitHub Actions
ssh-keygen -t rsa -b 4096 -C "github-actions-deploy" -f ~/.ssh/github_deploy_key

# НЕ создавайте passphrase (просто Enter)
```

### 2. Добавьте публичный ключ в GitHub

```bash
# Покажите публичный ключ
cat ~/.ssh/github_deploy_key.pub
```

В GitHub:
1. Settings → Deploy keys
2. Add deploy key
3. Вставьте публичный ключ
4. ✅ Allow write access

### 3. Добавьте приватный ключ в Secrets

```bash
# Покажите приватный ключ
cat ~/.ssh/github_deploy_key
```

В GitHub Secrets добавьте:
- `VDS_DEPLOY_KEY` - приватный ключ

### 4. Используйте в GitHub Actions

Измените `.github/workflows/deploy.yml`:

```yaml
- name: Deploy to server via SSH
  uses: appleboy/ssh-action@master
  with:
    host: ${{ secrets.VDS_HOST }}
    username: ${{ secrets.VDS_USERNAME }}
    key: ${{ secrets.VDS_DEPLOY_KEY }}
    script: |
      cd /var/www/apps/rlisystems_v1/python_version
      bash update.sh
      sudo systemctl restart rli-systems.service
```

---

## Вариант 3: Webhook + Скрипт на сервере 🪝

Самый простой способ без SSH:

### 1. Создайте скрипт на сервере

На вашем VDS сервере создайте файл `update_hook.php`:

```php
<?php
// Обновление из GitHub по webhook
$secret = 'YOUR_SECRET_KEY';
$repo = '/var/www/apps/rlisystems_v1/python_version';

$headers = getallheaders();
$hubSignature = $headers['X-Hub-Signature-256'] ?? '';

if ($hubSignature) {
    $payload = file_get_contents('php://input');
    $expectedSignature = 'sha256=' . hash_hmac('sha256', $payload, $secret);
    
    if (hash_equals($expectedSignature, $hubSignature)) {
        shell_exec("cd $repo && git pull && bash update.sh");
        http_response_code(200);
        echo "OK";
    }
}
?>
```

### 2. Настройте GitHub Webhook

В GitHub:
1. Settings → Webhooks → Add webhook
2. Payload URL: `https://your-server.com/update_hook.php`
3. Content type: `application/json`
4. Secret: `YOUR_SECRET_KEY`
5. Events: Just the push event

### 3. Проверьте работу

```bash
# На сервере
curl http://localhost/update_hook.php
```

---

## Вариант 4: GitHub Actions + GitHub Token 🔑

Используйте GitHub Personal Access Token:

### 1. Создайте Token

GitHub → Settings → Developer settings → Personal access tokens → Generate new token

Разрешения:
- ✅ repo (full control)
- ✅ workflow

### 2. Добавьте в Secrets

- `GITHUB_TOKEN` - ваш токен

### 3. Обновите workflow

```yaml
- name: Deploy via Git
  run: |
    git clone https://${{ secrets.GITHUB_TOKEN }}@github.com/yokiik/Vizit.git temp_repo
    cd temp_repo
    git checkout main
    # Копируйте файлы на сервер...
```

⚠️ **Не рекомендуется** для сложных деплоев.

---

## 🎯 Рекомендация

**Лучший вариант для вашего случая:** Вариант 2 (Deploy Key)

Почему:
- ✅ Безопасно (ключ создается на сервере)
- ✅ Не нужен SSH ключ с вашего компьютера
- ✅ Просто настроить
- ✅ Работает с GitHub Actions

---

## 📝 Пошаговая инструкция (Deploy Key)

### Шаг 1: Создайте ключ на сервере

```bash
ssh user@your-server

# Создайте ключ
ssh-keygen -t rsa -b 4096 -C "github-deploy" -f ~/.ssh/github_deploy_key

# Без passphrase (просто Enter, Enter)
```

### Шаг 2: Добавьте публичный ключ в GitHub

```bash
# На сервере
cat ~/.ssh/github_deploy_key.pub
# Скопируйте вывод
```

В GitHub:
1. Repo → Settings → Deploy keys
2. Add deploy key
3. Вставьте ключ
4. ✅ Allow write access
5. Add key

### Шаг 3: Добавьте приватный ключ в Secrets

```bash
# На сервере
cat ~/.ssh/github_deploy_key
# Скопируйте ВСЁ содержимое
```

В GitHub:
1. Settings → Secrets → Actions
2. New repository secret
3. Name: `VDS_DEPLOY_KEY`
4. Value: вставьте приватный ключ
5. Add secret

### Шаг 4: Обновите workflow (уже готово!)

Файлы `.github/workflows/deploy.yml` уже используют ключ из `VDS_SSH_KEY`, 
просто переименуйте секрет:

GitHub → Settings → Secrets → `VDS_SSH_KEY` → переименуйте в `VDS_DEPLOY_KEY`

Или оставьте как есть и используйте `VDS_SSH_KEY`.

### Шаг 5: Тестируйте

```bash
# Сделайте тестовый коммит
git add .
git commit -m "Test deploy"
git push
```

Проверьте: https://github.com/yokiik/Vizit/actions

---

## ✅ Готово!

Теперь при каждом `git push` код будет автоматически обновляться на сервере!

**Никакого SSH ключа с вашего компьютера не требуется!** 🎉


