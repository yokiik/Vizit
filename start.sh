#!/bin/bash

echo "===================================="
echo "RLI Systems v2 - Python Version"
echo "===================================="
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "[ОШИБКА] Python3 не найден!"
    echo "Установите Python 3.9 или выше"
    exit 1
fi

echo "[OK] Python найден"
echo ""

# Создание виртуального окружения
if [ ! -d "venv" ]; then
    echo "[INFO] Создание виртуального окружения..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ОШИБКА] Не удалось создать виртуальное окружение"
        exit 1
    fi
    echo "[OK] Виртуальное окружение создано"
    echo ""
fi

# Активация виртуального окружения
echo "[INFO] Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "[INFO] Проверка зависимостей..."
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "[ОШИБКА] Не удалось установить зависимости"
    exit 1
fi
echo "[OK] Зависимости установлены"
echo ""

# Запуск приложения
echo "[INFO] Запуск веб-сервера..."
echo "===================================="
echo ""
python3 main.py

