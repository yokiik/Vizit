// Глобальные переменные
let currentTasks = [];
let currentSettings = {};
let currentReferences = {};
let currentTab = 'tasks';
let currentReferenceType = 'operations';

// Функции для преобразования форматов дат
function convertDateDDMMToYYYYMMDD(ddmmDate) {
    if (!ddmmDate || ddmmDate.length < 5) return '';

    const [day, month] = ddmmDate.split('.');
    if (!day || !month) return '';

    const currentYear = new Date().getFullYear();
    return `${currentYear}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
}

function convertDateYYYYMMDDToDDMM(yyyymmddDate) {
    if (!yyyymmddDate) return '';

    const date = new Date(yyyymmddDate);
    if (isNaN(date.getTime())) return '';

    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    return `${day}.${month}`;
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupEventListeners();
    loadInitialData();
    setupResizeHandle();
}

// Настройка обработчиков событий
function setupEventListeners() {
    // Вкладки
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', (e) => {
            switchTab(e.target.dataset.tab);
        });
    });

    // Справочники
    document.querySelectorAll('.ref-tab-button').forEach(button => {
        button.addEventListener('click', (e) => {
            switchReferenceType(e.target.dataset.ref);
        });
    });

    // Кнопки управления
    document.getElementById('add-task-btn').addEventListener('click', async () => await openTaskModal());
    document.getElementById('start-automation-sequential-btn').addEventListener('click', () => startAutomation(false));
    document.getElementById('start-automation-parallel-btn').addEventListener('click', () => startAutomation(true));
    document.getElementById('stop-automation-btn').addEventListener('click', stopAutomation);
    document.getElementById('test-connection-btn').addEventListener('click', testConnection);
    document.getElementById('add-reference-btn').addEventListener('click', openReferenceModal);

    // Формы
    document.getElementById('task-form').addEventListener('submit', saveTask);
    document.getElementById('settings-form').addEventListener('submit', saveSettings);
    document.getElementById('reference-form').addEventListener('submit', saveReference);

    // Модальные окна
    document.querySelector('.close').addEventListener('click', closeTaskModal);
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            closeTaskModal();
        }
    });

    // Фильтры логов
    document.getElementById('log-level-filter').addEventListener('change', filterLogs);
    document.getElementById('log-category-filter').addEventListener('change', filterLogs);
    document.getElementById('clear-logs-btn').addEventListener('click', clearLogs);

    // Чекбокс сохранения логина и пароля
    document.getElementById('save-credentials').addEventListener('change', function(e) {
        const loginField = document.getElementById('login');
        const passwordField = document.getElementById('password');

        // Если чекбокс снят, очищаем поля логина и пароля
        if (!e.target.checked) {
            loginField.value = '';
            passwordField.value = '';
        }
    });
}

// Переключение вкладок
function switchTab(tabName) {
    // Скрыть все панели
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });

    // Убрать активное состояние с кнопок
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });

    // Показать нужную панель
    document.getElementById(tabName + '-tab').classList.add('active');

    // Активировать кнопку
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    currentTab = tabName;

    // Загрузить данные для вкладки
    switch(tabName) {
        case 'tasks':
            loadTasks();
            break;
        case 'settings':
            loadSettings();
            break;
        case 'references':
            loadReferences();
            break;
    }
}

// Переключение типа справочника
function switchReferenceType(refType) {
    document.querySelectorAll('.ref-tab-button').forEach(button => {
        button.classList.remove('active');
    });

    document.querySelector(`[data-ref="${refType}"]`).classList.add('active');
    currentReferenceType = refType;
    displayReferences();
}

// Загрузка начальных данных
function loadInitialData() {
    loadTasks();
    loadLogs();

    // Обновление данных: задания каждые 30 секунд, логи каждые 5 секунд
    setInterval(() => {
        if (currentTab === 'tasks') {
            loadTasks();
        }
    }, 30000);

    // Частое обновление логов для отслеживания автоматизации
    setInterval(() => {
        loadLogs();
    }, 5000);
}

// API запросы
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            // Создаем ошибку с дополнительной информацией о статусе
            const errorText = await response.text();
            const error = new Error(errorText || `HTTP error! status: ${response.status}`);
            error.status = response.status;
            error.statusText = response.statusText;
            throw error;
        }

        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }

        return await response.text();
    } catch (error) {
        console.error('API request error:', error);

        // Не показываем общее уведомление об ошибке здесь,
        // позволяем обработчикам самим решать, что показать
        throw error;
    }
}

// Загрузка заданий
async function loadTasks() {
    try {
        const tasks = await apiRequest('/api/tasks');
        // Сортируем задания по позиции (position) для правильного отображения порядка
        currentTasks = tasks.sort((a, b) => (a.position || 0) - (b.position || 0));
        displayTasks();
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

// Отображение заданий
function displayTasks() {
    const tbody = document.querySelector('#tasks-table tbody');
    tbody.innerHTML = '';

    currentTasks.forEach(task => {
        const row = createTaskRow(task);
        tbody.appendChild(row);
    });
}

// Создание строки задания
function createTaskRow(task) {
    const row = document.createElement('tr');
    row.draggable = true;
    row.dataset.taskId = task.id;
    row.classList.add('draggable-row');

    row.innerHTML = `
        <td class="drag-handle">⋮⋮</td>
        <td><input type="checkbox" ${task.in_work ? 'checked' : ''} onchange="toggleTaskInWork('${task.id}', this.checked)"></td>
        <td>${task.type_task}</td>
        <td><span class="status-badge ${task.status.toLowerCase()}">${task.status}</span></td>
        <td>${task.date}</td>
        <td>${task.time_slot}</td>
        <td>${task.num_auto}</td>
        <td>${task.driver}</td>
        <td>
            <button class="btn btn-small btn-primary" onclick="(async () => await editTask('${task.id}'))()">Изменить</button>
            <button class="btn btn-small btn-danger" onclick="deleteTask('${task.id}')">Удалить</button>
        </td>
    `;

    // Добавляем event listeners для drag & drop
    row.addEventListener('dragstart', handleDragStart);
    row.addEventListener('dragover', handleDragOver);
    row.addEventListener('dragenter', handleDragEnter);
    row.addEventListener('dragleave', handleDragLeave);
    row.addEventListener('drop', handleDrop);
    row.addEventListener('dragend', handleDragEnd);

    return row;
}

// Переключение состояния задания
async function toggleTaskInWork(taskId, inWork) {
    try {
        const task = currentTasks.find(t => t.id === taskId);
        if (task) {
            task.in_work = inWork;
            await apiRequest('/api/tasks/update', {
                method: 'PUT',
                body: JSON.stringify(task)
            });
        }
    } catch (error) {
        console.error('Error updating task:', error);
        loadTasks(); // Перезагрузить для отмены изменений
    }
}

// Открытие модального окна задания
async function openTaskModal(taskId = null) {
    const modal = document.getElementById('task-modal');
    const form = document.getElementById('task-form');
    const title = document.getElementById('task-modal-title');

    if (taskId) {
        const task = currentTasks.find(t => t.id === taskId);
        if (task) {
            // Асинхронно заполняем форму задания
            await fillTaskForm(task);
            title.textContent = 'Редактировать задание';
            form.dataset.taskId = taskId;
        }
    } else {
        // Для нового задания сначала заполняем выпадающие списки
        await populateTaskFormDropdowns();
        form.reset();
        title.textContent = 'Добавить задание';
        delete form.dataset.taskId;

        // Устанавливаем текущую дату по умолчанию
        const today = new Date();
        const dateString = today.getFullYear() + '-' +
            String(today.getMonth() + 1).padStart(2, '0') + '-' +
            String(today.getDate()).padStart(2, '0');
        document.getElementById('task-date').value = dateString;
    }

    modal.style.display = 'block';
}

// Заполнение выпадающих списков в форме задания данными из справочников
async function populateTaskFormDropdowns() {
    console.log('Заполняем выпадающие списки формы задания');
    console.log('currentReferences:', currentReferences);

    // Если справочники еще не загружены, пытаемся их загрузить
    if (!currentReferences || Object.keys(currentReferences).length === 0) {
        console.log('Справочники не загружены, загружаем...');
        await loadReferences();
    }

    // Заполняем типы операций
    populateSelect('task-type', 'operation_types');

    // Заполняем статусы
    populateSelect('task-status', 'statuses');

    // Заполняем временные слоты
    populateSelect('task-time-slot', 'time_slots');

    // Заполняем номера автомобилей
    populateSelect('task-auto', 'car_numbers');

    // Заполняем водителей
    populateSelect('task-driver', 'drivers');
}

// Универсальная функция для заполнения select'а данными из справочника
function populateSelect(selectId, referenceField) {
    const select = document.getElementById(selectId);
    if (!select) {
        console.warn(`Select элемент с id "${selectId}" не найден`);
        return;
    }

    if (!currentReferences) {
        console.warn('currentReferences не определен');
        return;
    }

    if (!currentReferences[referenceField]) {
        console.warn(`Справочник "${referenceField}" не найден в currentReferences:`, Object.keys(currentReferences));
        return;
    }

    // Сохраняем текущее значение
    const currentValue = select.value;
    console.log(`Сохраняем текущее значение для ${selectId}: "${currentValue}"`);

    // Очищаем все опции кроме первой (placeholder)
    const firstOption = select.querySelector('option[value=""]');
    select.innerHTML = '';
    if (firstOption) {
        select.appendChild(firstOption.cloneNode(true));
    }

    // Добавляем опции из справочника
    const items = currentReferences[referenceField];
    console.log(`Заполняем ${selectId} данными из ${referenceField}:`, items);

    items.forEach(item => {
        if (item.is_active !== false) { // Показываем все элементы, кроме явно неактивных
            const option = document.createElement('option');
            option.value = item.value;
            option.textContent = item.value;
            if (item.description) {
                option.textContent += ` - ${item.description}`;
            }
            select.appendChild(option);
        }
    });

    // Восстанавливаем значение если оно было
    if (currentValue) {
        select.value = currentValue;
        console.log(`Восстановлено значение для ${selectId}: "${currentValue}"`);
        if (select.value !== currentValue) {
            console.warn(`Не удалось восстановить значение "${currentValue}" для ${selectId}. Доступные опции:`, Array.from(select.options).map(opt => opt.value));
        }
    }

    console.log(`Заполнение ${selectId} завершено. Опций: ${select.options.length - 1}`);
}

// Заполнение формы задания
async function fillTaskForm(task) {
    const form = document.getElementById('task-form');

    // Сначала заполняем выпадающие списки и дожидаемся завершения
    await populateTaskFormDropdowns();

    // Затем заполняем значения из задания
    Object.keys(task).forEach(key => {
        const input = form.querySelector(`[name="${key}"]`);
        if (input) {
            if (input.type === 'checkbox') {
                input.checked = task[key];
            } else if (key === 'date' && input.type === 'date') {
                // Преобразуем дату из формата DD.MM в YYYY-MM-DD для календаря
                input.value = convertDateDDMMToYYYYMMDD(task[key]);
            } else {
                input.value = task[key] || '';
            }
        }
    });
}

// Закрытие модального окна
function closeTaskModal() {
    document.getElementById('task-modal').style.display = 'none';
}

// Сохранение задания
async function saveTask(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const taskData = Object.fromEntries(formData.entries());

    // Отладочная информация
    console.log('DEBUG: Form data before processing:', taskData);
    console.log('DEBUG: num_auto field value:', taskData.num_auto);
    console.log('DEBUG: driver field value:', taskData.driver);

    // Преобразование чекбокса
    taskData.in_work = form.querySelector('[name="in_work"]').checked;

    // Преобразование даты из формата YYYY-MM-DD в DD.MM для сервера
    if (taskData.date) {
        taskData.date = convertDateYYYYMMDDToDDMM(taskData.date);
    }

    // Проверяем критические поля
    if (!taskData.num_auto || taskData.num_auto === '') {
        showError('Поле "Номер авто" должно быть заполнено');
        return;
    }
    if (!taskData.driver || taskData.driver === '') {
        showError('Поле "Водитель" должно быть заполнено');
        return;
    }

    // Финальная отладочная информация
    console.log('DEBUG: Final taskData being sent to server:', taskData);

    try {
        const taskId = form.dataset.taskId;

        if (taskId) {
            // Обновление существующего задания
            taskData.id = taskId;
            console.log('DEBUG: Updating task with data:', taskData);
            await apiRequest('/api/tasks/update', {
                method: 'PUT',
                body: JSON.stringify(taskData)
            });
        } else {
            // Создание нового задания
            console.log('DEBUG: Creating new task with data:', taskData);
            await apiRequest('/api/tasks/create', {
                method: 'POST',
                body: JSON.stringify(taskData)
            });
        }

        closeTaskModal();
        loadTasks();
        showSuccess('Задание сохранено успешно');
    } catch (error) {
        console.error('Error saving task:', error);
        showError('Ошибка при сохранении задания');
    }
}

// Редактирование задания
async function editTask(taskId) {
    await openTaskModal(taskId);
}

// Удаление задания
async function deleteTask(taskId) {
    if (!confirm('Вы уверены, что хотите удалить это задание?')) {
        return;
    }

    try {
        await apiRequest(`/api/tasks/delete?id=${taskId}`, {
            method: 'DELETE'
        });

        loadTasks();
        showSuccess('Задание удалено успешно');
    } catch (error) {
        console.error('Error deleting task:', error);
        showError('Ошибка при удалении задания');
    }
}

// Запуск автоматизации
async function startAutomation(isParallel = false) {
    const selectedTasks = currentTasks.filter(task => task.in_work);

    if (selectedTasks.length === 0) {
        showError('Выберите задания для выполнения (установите флажок "В работе")');
        return;
    }

    const requestData = {
        taskIds: selectedTasks.map(task => task.id),
        sequential: !isParallel,
        parallel: isParallel
    };

    // Если параллельное выполнение, добавляем количество одновременных заданий
    if (isParallel) {
        const maxConcurrency = parseInt(document.getElementById('max-concurrency').value) || 5;
        requestData.maxConcurrency = maxConcurrency;
    }

    try {
        await apiRequest('/api/automation/start', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });

        updateAutomationStatus('running');
        
        const mode = isParallel ? `параллельно (макс. ${requestData.maxConcurrency || 5} одновременно)` : 'поочередно';
        showSuccess(`🚀 Автоматизация запущена для ${selectedTasks.length} заданий. Обработка будет происходить ${mode}.`);
    } catch (error) {
        console.error('Error starting automation:', error);
        showError('Ошибка при запуске автоматизации: ' + error.message);
    }
}

// Остановка автоматизации
async function stopAutomation() {
    try {
        await apiRequest('/api/automation/stop', {
            method: 'POST'
        });

        updateAutomationStatus('stopped');
        showSuccess('Автоматизация остановлена');
    } catch (error) {
        console.error('Error stopping automation:', error);
        showError('Ошибка при остановке автоматизации');
    }
}

// Обновление статуса автоматизации
function updateAutomationStatus(status) {
    const statusElement = document.getElementById('automation-status');
    statusElement.className = `status ${status}`;
    statusElement.textContent = status === 'running' ? 'Выполняется' : 'Остановлено';
}

// Загрузка настроек
async function loadSettings() {
    try {
        const settings = await apiRequest('/api/settings');
        currentSettings = settings;
        displaySettings();
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

// Отображение настроек
function displaySettings() {
    const form = document.getElementById('settings-form');

    Object.keys(currentSettings).forEach(key => {
        const input = form.querySelector(`[name="${key}"]`);

        if (input && key !== 'useHeadless') {
            // Для чекбокса save_credentials
            if (input.type === 'checkbox') {
                input.checked = currentSettings[key];
            }
            // Для логина и пароля - показываем только если включено сохранение
            else if ((key === 'login' || key === 'password')) {
                if (currentSettings.save_credentials) {
                    input.value = currentSettings[key] || '';
                } else {
                    input.value = ''; // Очищаем поля если не сохраняем
                }
            }
            // Для остальных полей
            else {
                // Если значение с сервера пустое, а в поле уже есть значение по умолчанию, не перезаписываем
                if (currentSettings[key] || !input.value) {
                    input.value = currentSettings[key] || '';
                }
            }
        }
    });

    // Устанавливаем значения по умолчанию для новых полей если они не заданы
    if (!form.querySelector('[name="browser_width"]').value) {
        form.querySelector('[name="browser_width"]').value = '1280';
    }
    if (!form.querySelector('[name="browser_height"]').value) {
        form.querySelector('[name="browser_height"]').value = '720';
    }
    if (!form.querySelector('[name="default_execution_attempts"]').value) {
        form.querySelector('[name="default_execution_attempts"]').value = '50';
    }
    if (!form.querySelector('[name="element_timeout"]').value) {
        form.querySelector('[name="element_timeout"]').value = '10';
    }
    if (!form.querySelector('[name="refresh_interval"]').value) {
        form.querySelector('[name="refresh_interval"]').value = '60';
    }
}

// Сохранение настроек
async function saveSettings(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const settingsData = Object.fromEntries(formData.entries());

    // Преобразование чекбокса save_credentials
    settingsData.save_credentials = form.querySelector('[name="save_credentials"]').checked;

    // Если не сохраняем credentials, очищаем логин и пароль в данных для отправки
    if (!settingsData.save_credentials) {
        settingsData.login = '';
        settingsData.password = '';
    }

    // Преобразование чисел
    settingsData.use_headless = false; // Всегда отключаем headless режим
    settingsData.refresh_interval = parseInt(settingsData.refresh_interval) || 60;
    settingsData.browser_width = parseInt(settingsData.browser_width) || 1280;
    settingsData.browser_height = parseInt(settingsData.browser_height) || 720;
    settingsData.default_execution_attempts = parseInt(settingsData.default_execution_attempts) || 60;
    settingsData.default_delay_try = parseInt(settingsData.default_delay_try) || 60;
    settingsData.element_timeout = parseInt(settingsData.element_timeout) || 10;

    try {
        await apiRequest('/api/settings', {
            method: 'POST',
            body: JSON.stringify(settingsData)
        });

        currentSettings = settingsData;
        showSuccess('Настройки сохранены успешно');

        // Если отключили сохранение credentials, очищаем поля в форме
        if (!settingsData.save_credentials) {
            form.querySelector('[name="login"]').value = '';
            form.querySelector('[name="password"]').value = '';
        }

    } catch (error) {
        console.error('Error saving settings:', error);
        showError('Ошибка при сохранении настроек');
    }
}

// Проверка подключения
async function testConnection() {
    const button = document.getElementById('test-connection-btn');
    const originalText = button.textContent;

    button.textContent = 'Проверяется...';
    button.disabled = true;

    try {
        // Собираем данные из формы настроек
        const form = document.getElementById('settings-form');
        const formData = new FormData(form);
        const settingsData = Object.fromEntries(formData.entries());

        // Проверяем обязательные поля
        if (!settingsData.site_url) {
            showError('Введите URL сайта');
            return;
        }
        if (!settingsData.login) {
            showError('Введите логин');
            return;
        }
        if (!settingsData.password) {
            showError('Введите пароль');
            return;
        }

        // Преобразование данных
        settingsData.use_headless = false; // Принудительно показываем браузер для теста
        settingsData.refresh_interval = parseInt(settingsData.refresh_interval) || 10;
        settingsData.browser_width = parseInt(settingsData.browser_width) || 1280;
        settingsData.browser_height = parseInt(settingsData.browser_height) || 720;
        settingsData.default_execution_attempts = 50;
        settingsData.element_timeout = 10;

        // Преобразование чекбокса save_credentials в булевое значение
        settingsData.save_credentials = form.querySelector('[name="save_credentials"]').checked;
        
        // Добавляем недостающие поля с значениями по умолчанию
        settingsData.default_delay_try = parseInt(settingsData.default_delay_try) || 60; // в секундах
        settingsData.slot_check_attempts = 10; // значение по умолчанию
        settingsData.slot_check_interval = 5; // значение по умолчанию
        settingsData.connection_status = false; // значение по умолчанию
        settingsData.last_connection_test = new Date().toISOString(); // текущее время
        settingsData.created_at = new Date().toISOString(); // текущее время
        settingsData.updated_at = new Date().toISOString(); // текущее время

        showSuccess('Запускается браузер для проверки подключения...');

        // Отладочная информация
        console.log('Отправляемые данные:', settingsData);
        console.log('JSON строка:', JSON.stringify(settingsData));

        // Отправляем запрос на проверку подключения
        const result = await apiRequest('/api/connection/test', {
            method: 'POST',
            body: JSON.stringify(settingsData)
        });

        if (result.success) {
            updateConnectionStatus('connected');
            showSuccess(`Подключение успешно! ${result.message || ''}`);
        } else {
            updateConnectionStatus('disconnected');
            showError(`Ошибка подключения: ${result.error || 'Неизвестная ошибка'}`);
        }

    } catch (error) {
        updateConnectionStatus('disconnected');
        showError('Ошибка проверки подключения: ' + error.message);
    } finally {
        button.textContent = originalText;
        button.disabled = false;
    }
}



// Обновление статуса подключения
function updateConnectionStatus(status) {
    const statusElement = document.getElementById('connection-status');
    statusElement.className = `status ${status}`;
    statusElement.textContent = status === 'connected' ? 'Подключено' : 'Отключено';
}

// Загрузка справочников
async function loadReferences() {
    try {
        const references = await apiRequest('/api/references');
        currentReferences = references;
        console.log('Справочники загружены:', currentReferences);
        displayReferences();

        // Обновляем выпадающие списки в форме задания, если она открыта
        const taskModal = document.getElementById('task-modal');
        if (taskModal && taskModal.style.display === 'block') {
            console.log('Обновляем выпадающие списки в открытой форме');
            populateTaskFormDropdowns();
        }
    } catch (error) {
        console.error('Error loading references:', error);
    }
}

// Отображение справочников
function displayReferences() {
    const container = document.getElementById('reference-list');
    container.innerHTML = '';

    // Получаем правильное поле данных для текущего типа справочника
    const referenceField = getReferenceFieldName(currentReferenceType);
    const items = currentReferences[referenceField];

    if (!items || items.length === 0) {
        container.innerHTML = '<p class="no-data">Справочник пуст. Нажмите "Добавить" для создания первой записи.</p>';
        return;
    }

    items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'reference-item';
        div.innerHTML = `
            <div class="reference-item-content">
                <span class="reference-value">${item.value}</span>
                ${item.description ? `<span class="reference-description"> - ${item.description}</span>` : ''}
            </div>
            <button class="btn btn-small btn-danger" onclick="deleteReferenceItem('${item.id}')">Удалить</button>
        `;
        container.appendChild(div);
    });
}

// Получение названия поля в JSON для типа справочника
function getReferenceFieldName(referenceType) {
    const fieldMapping = {
        'operations': 'operation_types',
        'statuses': 'statuses',
        'timeslots': 'time_slots',
        'autos': 'car_numbers',
        'drivers': 'drivers',
        'contracts': 'terminal_contracts'
    };

    return fieldMapping[referenceType] || 'operation_types';
}

// Загрузка логов
async function loadLogs() {
    try {
        const logs = await apiRequest('/api/logs');
        displayLogs(logs);
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

// Отображение логов
function displayLogs(logs) {
    const container = document.getElementById('logs-content');
    const wasAtBottom = container.scrollTop >= (container.scrollHeight - container.clientHeight - 50);

    container.innerHTML = '';

    logs.forEach(log => {
        const div = document.createElement('div');
        div.className = `log-entry ${log.level.toLowerCase()}`;
        div.innerHTML = `
            <div class="log-timestamp">${formatTimestamp(log.timestamp)}</div>
            <div class="log-category">${log.category}</div>
            <div class="log-message">${log.message}</div>
        `;
        container.appendChild(div);
    });

    // Автопрокрутка к последнему сообщению (только если пользователь был внизу)
    if (wasAtBottom || logs.length === 1) {
        container.scrollTop = container.scrollHeight;
    }
}

// Фильтрация логов
function filterLogs() {
    const levelFilter = document.getElementById('log-level-filter').value;
    const categoryFilter = document.getElementById('log-category-filter').value;

    const entries = document.querySelectorAll('.log-entry');

    entries.forEach(entry => {
        let show = true;

        if (levelFilter && !entry.classList.contains(levelFilter.toLowerCase())) {
            show = false;
        }

        if (categoryFilter) {
            const category = entry.querySelector('.log-category').textContent;
            if (category !== categoryFilter) {
                show = false;
            }
        }

        entry.style.display = show ? 'block' : 'none';
    });
}

// Очистка логов
function clearLogs() {
    if (confirm('Очистить все логи?')) {
        document.getElementById('logs-content').innerHTML = '';
    }
}

// Настройка изменения размера панелей
function setupResizeHandle() {
    const resizeHandle = document.querySelector('.resize-handle');
    const leftPanel = document.querySelector('.left-panel');
    const rightPanel = document.querySelector('.right-panel');

    let isResizing = false;

    resizeHandle.addEventListener('mousedown', (e) => {
        isResizing = true;
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
    });

    function handleMouseMove(e) {
        if (!isResizing) return;

        const containerWidth = document.querySelector('.main-content').offsetWidth;
        const leftWidth = (e.clientX / containerWidth) * 100;

        if (leftWidth > 30 && leftWidth < 80) {
            leftPanel.style.flex = `0 0 ${leftWidth}%`;
        }
    }

    function handleMouseUp() {
        isResizing = false;
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
    }
}

// Утилиты
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('ru-RU');
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showError(message) {
    showNotification(message, 'error');
}

function showNotification(message, type) {
    // Простая реализация уведомлений
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background-color: ${type === 'success' ? '#27ae60' : '#e74c3c'};
        color: white;
        border-radius: 6px;
        z-index: 10000;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: opacity 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// ===== ФУНКЦИИ ДЛЯ РАБОТЫ СО СПРАВОЧНИКАМИ =====

// Открытие модального окна для добавления записи в справочник
function openReferenceModal() {
    const modal = document.getElementById('reference-modal');
    const form = document.getElementById('reference-form');
    const title = document.getElementById('reference-modal-title');

    // Получаем название текущего справочника
    const referenceTypeName = getReferenceTypeName(currentReferenceType);
    title.textContent = `Добавить запись в "${referenceTypeName}"`;

    // Очищаем форму
    form.reset();

    // Показываем модальное окно
    modal.style.display = 'block';
}

// Закрытие модального окна справочника
function closeReferenceModal() {
    document.getElementById('reference-modal').style.display = 'none';
}

// Сохранение записи в справочник
async function saveReference(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const referenceData = {
        type: currentReferenceType,
        value: formData.get('value').trim(), // Убираем лишние пробелы
        description: formData.get('description').trim() || ''
    };

    // Простая валидация на стороне клиента
    if (!referenceData.value) {
        showError('Поле "Значение" не может быть пустым');
        return;
    }

    if (referenceData.value.length > 100) {
        showError('Значение не может быть длиннее 100 символов');
        return;
    }

    if (referenceData.description.length > 255) {
        showError('Описание не может быть длиннее 255 символов');
        return;
    }

    try {
        const response = await apiRequest('/api/references/add', {
            method: 'POST',
            body: JSON.stringify(referenceData)
        });

        closeReferenceModal();
        loadReferences(); // Перезагружаем справочники
        showSuccess(`✅ Запись "${referenceData.value}" успешно добавлена в справочник`);

    } catch (error) {
        console.error('Error saving reference:', error);

        // Обработка различных типов ошибок
        if (error.status === 409) { // Conflict - дубликат
            showError(`❌ Запись с таким значением уже существует: "${referenceData.value}"`);
            // Подсвечиваем поле ввода
            highlightErrorField('reference-value');
        } else if (error.status === 400) { // Bad Request - ошибка валидации
            showError(`❌ Ошибка валидации: ${error.message}`);
        } else {
            showError(`❌ Ошибка при сохранении записи: ${error.message}`);
        }
    }
}

// Удаление записи из справочника
async function deleteReferenceItem(itemId) {
    if (!confirm('Вы уверены, что хотите удалить эту запись?')) {
        return;
    }

    try {
        await apiRequest('/api/references/delete', {
            method: 'DELETE',
            body: JSON.stringify({
                type: currentReferenceType,
                itemId: itemId
            })
        });

        loadReferences(); // Перезагружаем справочники
        showSuccess('Запись удалена из справочника');
    } catch (error) {
        console.error('Error deleting reference item:', error);
        showError('Ошибка при удалении записи: ' + error.message);
    }
}

// Получение названия типа справочника для отображения
function getReferenceTypeName(referenceType) {
    const typeNames = {
        'operations': 'Операции',
        'statuses': 'Статусы',
        'timeslots': 'Временные слоты',
        'autos': 'Госномера автомобилей',
        'drivers': 'Водители',
        'contracts': 'Договоры с терминалом'
    };

    return typeNames[referenceType] || 'Справочник';
}

// Переключение типа справочника
function switchReferenceType(referenceType) {
    currentReferenceType = referenceType;

    // Обновляем активную вкладку
    document.querySelectorAll('.ref-tab-button').forEach(button => {
        button.classList.remove('active');
    });
    document.querySelector(`[data-ref="${referenceType}"]`).classList.add('active');

    // Обновляем отображение справочника
    displayReferences();
}

// Подсветка поля с ошибкой
function highlightErrorField(fieldId) {
    const field = document.getElementById(fieldId);
    if (field) {
        field.style.borderColor = '#e74c3c';
        field.style.boxShadow = '0 0 5px rgba(231, 76, 60, 0.5)';

        // Убираем подсветку при следующем вводе
        field.addEventListener('input', function removeHighlight() {
            field.style.borderColor = '';
            field.style.boxShadow = '';
            field.removeEventListener('input', removeHighlight);
        }, { once: true });

        // Автоматически убираем подсветку через 5 секунд
        setTimeout(() => {
            field.style.borderColor = '';
            field.style.boxShadow = '';
        }, 5000);
    }
}

// Drag & Drop функциональность для заданий
let draggedRow = null;

function handleDragStart(e) {
    draggedRow = this;
    this.classList.add('dragging');

    // Устанавливаем данные для передачи
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.outerHTML);
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault(); // Позволяет drop
    }

    e.dataTransfer.dropEffect = 'move';

    // Добавляем визуальную индикацию
    this.classList.add('drag-over');

    return false;
}

function handleDragEnter(e) {
    this.classList.add('drag-over');
}

function handleDragLeave(e) {
    this.classList.remove('drag-over');
}

function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation(); // Останавливает перенаправления
    }

    if (draggedRow !== this) {
        // Получаем таблицу и все строки
        const tbody = document.querySelector('#tasks-table tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));

        const draggedIndex = rows.indexOf(draggedRow);
        const targetIndex = rows.indexOf(this);

        // Перемещаем элемент в DOM
        if (draggedIndex < targetIndex) {
            tbody.insertBefore(draggedRow, this.nextSibling);
        } else {
            tbody.insertBefore(draggedRow, this);
        }

        // Обновляем позиции заданий
        updateTaskPositions();
    }

    this.classList.remove('drag-over');
    return false;
}

function handleDragEnd(e) {
    // Убираем все визуальные индикаторы
    const rows = document.querySelectorAll('#tasks-table tbody tr');
    rows.forEach(row => {
        row.classList.remove('dragging', 'drag-over');
    });

    draggedRow = null;
}

// Обновление позиций заданий на сервере
async function updateTaskPositions() {
    try {
        const tbody = document.querySelector('#tasks-table tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));

        const taskPositions = {};
        rows.forEach((row, index) => {
            const taskId = row.dataset.taskId;
            if (taskId) {
                taskPositions[taskId] = index + 1; // Позиции начинаются с 1
            }
        });

        // Отправляем обновленные позиции на сервер
        await apiRequest('/api/tasks/reorder', {
            method: 'POST',
            body: JSON.stringify({ task_positions: taskPositions })
        });

        // Обновляем локальный список заданий
        updateLocalTaskPositions(taskPositions);

        showSuccess('✅ Порядок заданий обновлен');

    } catch (error) {
        console.error('Error updating task positions:', error);
        showError('❌ Ошибка при обновлении порядка заданий');

        // Перезагружаем задания для восстановления исходного порядка
        loadTasks();
    }
}

// Обновление локального списка заданий с новыми позициями
function updateLocalTaskPositions(taskPositions) {
    currentTasks.forEach(task => {
        if (taskPositions[task.id] !== undefined) {
            task.position = taskPositions[task.id];
        }
    });

    // Сортируем по новым позициям
    currentTasks.sort((a, b) => (a.position || 0) - (b.position || 0));
}