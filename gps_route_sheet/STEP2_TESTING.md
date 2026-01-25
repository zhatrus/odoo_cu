# Крок 2: Тестування розширення fleet.vehicle з GPS полями

## Що зроблено:
1. ✅ Розширено модель `fleet.vehicle` з GPS полями
2. ✅ Додано computed fields для поточної GPS позиції
3. ✅ Створено методи в `gps.db.service` для отримання даних
4. ✅ Створено views (form, tree, search) з GPS полями

## Команди для тестування на VM:

### 1. Pull останніх змін з GitHub
```bash
cd /home/mini/odoo/odoo19/repositories/odoo_cu
git pull
```

### 2. Оновити модуль
```bash
odoo-helper addons update gps_route_sheet
```

### 3. Перезапустити Odoo
```bash
odoo-helper restart
```

### 4. Перевірити в UI:
- Відкрити: **Fleet → Vehicles**
- Відкрити будь-яке авто
- Перевірити наявність вкладки **"GPS Tracking"**
- Заповнити поля:
  - GPS IMEI: `350317172983730` (з вашої БД)
  - Tracker S/N: `1130512237`
  - Fuel Card Number: `7825390000619140`
  - Fuel Norm: `9.80`

### 5. Перевірити computed fields:
- Після збереження перевірити чи з'являються:
  - GPS Status
  - Current Latitude/Longitude
  - Last Position Time

### 6. Перевірити tree view:
- В списку авто повинні бути колонки IMEI та GPS Status

### 7. Перевірити search:
- Фільтри: "Has GPS Tracker", "No GPS Tracker", "GPS Active"

## Очікувані результати:
✅ Вкладка GPS Tracking відображається  
✅ Всі поля доступні для редагування  
✅ Computed fields показують дані з PostgreSQL  
✅ Tree view показує IMEI та статус  
✅ Search фільтри працюють  

## Можливі проблеми:
1. **GPS Status = "Error"**: Перевірити налаштування підключення до PostgreSQL БД
2. **Вкладка не відображається**: Очистити кеш браузера
3. **Помилка при оновленні**: Перевірити логи `odoo-helper server log`

## Наступний крок:
Після успішного тестування переходимо до **Кроку 3: Wizard синхронізації авто**
