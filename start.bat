@echo off
chcp 65001 > nul
echo ====================================
echo RLI Systems v2 - Python Version
echo ====================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python 3.9 или выше с https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python найден
echo.

REM Проверка виртуального окружения
if not exist "venv\" (
    echo [INFO] Создание виртуального окружения...
    python -m venv venv
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось создать виртуальное окружение
        pause
        exit /b 1
    )
    echo [OK] Виртуальное окружение создано
    echo.
)

REM Активация виртуального окружения
echo [INFO] Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Установка зависимостей
echo [INFO] Проверка зависимостей...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить зависимости
    pause
    exit /b 1
)
echo [OK] Зависимости установлены
echo.

REM Запуск приложения
echo [INFO] Запуск веб-сервера...
echo ====================================
echo.
python main.py

pause

