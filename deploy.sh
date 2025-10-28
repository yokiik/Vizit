#!/bin/bash

# Скрипт автообновления с GitHub
# Запуск: ./deploy.sh или через cron

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   RLI Systems - Auto Deploy Script    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Получаем путь к директории скрипта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || exit 1

# Проверяем, что мы в правильной директории
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Ошибка: main.py не найден!${NC}"
    echo -e "${RED}   Запустите скрипт из директории проекта${NC}"
    exit 1
fi

# Сохраняем текущую версию
CURRENT_VERSION=$(git rev-parse HEAD 2>/dev/null)
CURRENT_DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo -e "${YELLOW}📅 Дата: ${CURRENT_DATE}${NC}"
echo -e "${YELLOW}📦 Текущая версия: ${CURRENT_VERSION}${NC}"
echo ""

# Получаем последние изменения
echo -e "${YELLOW}📥 Получаем последние изменения из GitHub...${NC}"
git fetch origin || {
    echo -e "${RED}❌ Ошибка при получении изменений из Git${NC}"
    exit 1
}

# Проверяем, есть ли новые изменения
LATEST_VERSION=$(git rev-parse origin/master 2>/dev/null)

if [ -z "$LATEST_VERSION" ]; then
    echo -e "${RED}❌ Не удалось получить последнюю версию${NC}"
    exit 1
fi

if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
    echo -e "${GREEN}✅ У вас уже последняя версия!${NC}"
    echo -e "${GREEN}   Версия: ${CURRENT_VERSION}${NC}"
    exit 0
fi

echo -e "${YELLOW}🔄 Найдены новые изменения!${NC}"
echo -e "${YELLOW}   Обновляем: ${CURRENT_VERSION:0:8} → ${LATEST_VERSION:0:8}${NC}"
echo ""

# Делаем бэкап текущей версии
echo -e "${YELLOW}💾 Создаем резервную копию...${NC}"
mkdir -p backup
BACKUP_FILE="backup/backup_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$BACKUP_FILE" . --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='backup' 2>/dev/null
echo -e "${GREEN}✓ Резервная копия создана: ${BACKUP_FILE}${NC}"

# Обновляем код
echo -e "${YELLOW}📦 Обновляем код...${NC}"
git stash 2>/dev/null
git pull origin master || {
    echo -e "${RED}❌ Ошибка при обновлении кода${NC}"
    git stash pop 2>/dev/null
    exit 1
}
echo -e "${GREEN}✓ Код обновлен${NC}"

# Проверяем, есть ли виртуальное окружение
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}🔧 Создаем виртуальное окружение...${NC}"
    python3 -m venv venv || {
        echo -e "${RED}❌ Ошибка создания виртуального окружения${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ Виртуальное окружение создано${NC}"
fi

# Активируем виртуальное окружение
echo -e "${YELLOW}🔌 Активируем виртуальное окружение...${NC}"
source venv/bin/activate || {
    echo -e "${RED}❌ Ошибка активации виртуального окружения${NC}"
    exit 1
}

# Обновляем зависимости
echo -e "${YELLOW}📦 Обновляем зависимости...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt || {
    echo -e "${RED}❌ Ошибка установки зависимостей${NC}"
    exit 1
}
echo -e "${GREEN}✓ Зависимости обновлены${NC}"

# Устанавливаем gunicorn если его нет
echo -e "${YELLOW}📦 Проверяем gunicorn...${NC}"
pip install -q gunicorn || {
    echo -e "${RED}❌ Ошибка установки gunicorn${NC}"
    exit 1
}

# Перезапускаем приложение (только если используется systemd)
if systemctl is-active --quiet rli-systems.service 2>/dev/null; then
    echo -e "${YELLOW}🔄 Перезапускаем приложение...${NC}"
    sudo systemctl restart rli-systems.service || {
        echo -e "${RED}❌ Ошибка перезапуска сервиса${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ Приложение перезапущено${NC}"
else
    echo -e "${YELLOW}⚠️  Systemd сервис не запущен, пропускаем перезапуск${NC}"
fi

# Проверяем статус
echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}✅ Обновление завершено успешно!${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📊 Информация о версиях:${NC}"
echo -e "   ${YELLOW}Предыдущая:${NC} ${CURRENT_VERSION:0:8}"
echo -e "   ${YELLOW}Текущая:${NC}    ${LATEST_VERSION:0:8}"
echo ""

# Очищаем старые бэкапы (старше 7 дней)
if [ -d "backup" ]; then
    echo -e "${YELLOW}🧹 Очищаем старые бэкапы...${NC}"
    find backup -name "*.tar.gz" -mtime +7 -delete 2>/dev/null
fi

echo -e "${GREEN}✓ Готово!${NC}"

