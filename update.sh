#!/bin/bash

# Скрипт обновления для автоматического деплоя через GitHub Actions
# Расположение: /var/www/apps/rlisystems_v1/python_version/update.sh

set -e  # Остановка при ошибке

echo "=========================================="
echo "RLI Systems - Обновление приложения"
echo "=========================================="
echo ""

# Переходим в директорию проекта
cd "$(dirname "$0")" || exit 1

echo "[1/6] Получение изменений из GitHub..."
git fetch origin || {
    echo "❌ Ошибка: не удалось получить изменения из Git"
    exit 1
}

echo "[2/6] Применение изменений..."
git reset --hard origin/main || git reset --hard origin/master || {
    echo "❌ Ошибка: не удалось обновить код"
    exit 1
}
git pull || {
    echo "❌ Ошибка: не удалось применить изменения"
    exit 1
}

echo "[3/6] Активация виртуального окружения..."
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv || {
        echo "❌ Ошибка: не удалось создать виртуальное окружение"
        exit 1
    }
fi

source venv/bin/activate || {
    echo "❌ Ошибка: не удалось активировать виртуальное окружение"
    exit 1
}

echo "[4/6] Обновление зависимостей..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet || {
    echo "❌ Ошибка: не удалось установить зависимости"
    exit 1
}

echo "[5/6] Проверка установки uvicorn..."
pip show uvicorn >/dev/null 2>&1 || {
    echo "⚠️  Предупреждение: uvicorn не найден, но должен быть в requirements.txt"
}

echo "[6/6] Обновление завершено успешно!"
echo ""
echo "Следующий шаг: перезапуск systemd сервиса rli-systems.service"

