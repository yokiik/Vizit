# 🚀 Самый простой способ деплоя

## SSH ключ с вашего компьютера НЕ нужен!

Вместо этого создайте ключ прямо на сервере:

## Пошаговая инструкция

### 1️⃣ Подключитесь к VDS серверу

```bash
ssh user@your-server-ip
```

### 2️⃣ Создайте SSH ключ на сервере

```bash
# Создайте ключ специально для GitHub
ssh-keygen -t rsa -b 4096 -C "github-deploy" -f ~/.ssh/github_deploy_key

# Когда спросит passphrase - просто нажмите Enter дважды
# (Без пароля!)
```

### 3️⃣ Скопируйте публичный ключ

```bash
# Покажите публичный ключ
cat ~/.ssh/github_deploy_key.pub
```

Скопируйте вывод в буфер обмена.

### 4️⃣ Добавьте ключ в GitHub

1. Откройте: https://github.com/yokiik/Vizit/settings/keys
2. Нажмите "Add deploy key"
3. Вставьте публичный ключ
4. ✅ **Отметьте "Allow write access"**
5. "Add key"

### 5️⃣ Скопируйте приватный ключ

```bash
# На сервере
cat ~/.ssh/github_deploy_key
```

Скопируйте **ВСЁ** содержимое в буфер обмена.

### 6️⃣ Добавьте в GitHub Secrets

1. Откройте: https://github.com/yokiik/Vizit/settings/secrets/actions
2. "New repository secret"
3. **Name:** `VDS_SSH_KEY`
4. **Value:** вставьте приватный ключ
5. "Add secret"

### 7️⃣ Добавьте серверные данные

Еще два секрета:

**Имя:** `VDS_HOST`
**Значение:** IP вашего сервера

**Имя:** `VDS_USERNAME`
**Значение:** имя пользователя на сервере (обычно `root` или `ubuntu`)

### 8️⃣ Готово!

Теперь сделайте коммит:

```bash
git add .
git commit -m "Setup deploy"
git push
```

И проверьте: https://github.com/yokiik/Vizit/actions

---

## ✅ Всё! Никакого SSH ключа с вашего компьютера не требуется!

Ключ создается и хранится только на сервере.


