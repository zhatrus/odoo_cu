# Крок 3: Тестування Wizard синхронізації авто

## Що зроблено:
1. ✅ Створено TransientModel `vehicle.sync.wizard`
2. ✅ Додано метод `fetch_vehicles()` в `gps.db.service`
3. ✅ Створено wizard view з 3 режимами синхронізації
4. ✅ Додано action та menu item
5. ✅ Оновлено права доступу в ir.model.access.csv

## Команди для оновлення на VM:

```bash
# 1. Pull змін
cd /home/mini/odoo/odoo19/repositories/odoo_cu
git pull

# 2. Оновити модуль
odoo-helper restart --update gps_route_sheet
```

## Перевірка в UI:

### 1. Відкрити wizard через меню:
- **Fleet → Configuration → Sync Vehicles from GPS**

### 2. Або через Action на списку авто:
- **Fleet → Vehicles** → Action → **Sync Vehicles from GPS DB**

### 3. В wizard:
- Вибрати режим синхронізації:
  - **Create New Vehicles Only** - тільки нові
  - **Update Existing Vehicles** - тільки оновлення
  - **Create New and Update Existing** - обидва (рекомендовано)
- Натиснути **Synchronize**

### 4. Очікуваний результат:
- Notification: "Synchronization Successful"
- Показує статистику:
  - Created: X
  - Updated: Y
  - Skipped: Z
  - Total processed: N
- Кнопка **View Vehicles** → список авто з GPS

### 5. Перевірити в списку авто:
- Повинні з'явитися авто з вашої PostgreSQL БД
- IMEI заповнені
- Номерні знаки (license_plate)
- Паливні картки

## Режими синхронізації:

### Create New Vehicles Only:
- Створює тільки нові авто (якщо IMEI не існує)
- Пропускає існуючі

### Update Existing Vehicles:
- Оновлює тільки існуючі авто (по IMEI)
- Пропускає нові

### Create New and Update Existing:
- Створює нові + оновлює існуючі
- Рекомендований режим для першого запуску

## Можливі проблеми:

### "GPS database connection is not configured"
Налаштувати підключення:
- Settings → Technical → Parameters → System Parameters
- Додати параметри:
  - `gps_route_sheet.db_host` = localhost
  - `gps_route_sheet.db_port` = 5432
  - `gps_route_sheet.db_name` = your_gps_db
  - `gps_route_sheet.db_user` = your_user
  - `gps_route_sheet.db_password` = your_password

### "No vehicles found in GPS database"
- Перевірити чи є дані в таблиці `vehicles`
- Перевірити підключення до PostgreSQL

## Наступний крок:
Після успішної синхронізації переходимо до **Кроку 4: Демо дані + переклад UK**
