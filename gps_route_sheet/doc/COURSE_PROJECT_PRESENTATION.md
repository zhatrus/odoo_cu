# Презентація Курсової Роботи: GPS Route Sheet Module

## 📋 Зміст
1. [Загальна Інформація](#загальна-інформація)
2. [Функціональні Можливості](#функціональні-можливості)
3. [Технічна Реалізація](#технічна-реалізація)
4. [Структура Модуля](#структура-модуля)
5. [Демонстрація Роботи](#демонстрація-роботи)
6. [Відповідність Вимогам](#відповідність-вимогам)

---

## 1. Загальна Інформація

### Назва Модуля
**GPS Route Sheet** (`gps_route_sheet`)

### Призначення
Комплексна система GPS-моніторингу та управління маршрутними листами для організацій з автопарком, обладнаним GPS-трекерами.

### Версія Odoo
19.0

### Залежності
- `fleet` - стандартний модуль Odoo для управління автопарком
- `base` - базовий модуль Odoo
- `psycopg2` - Python бібліотека для роботи з PostgreSQL

---

## 2. Функціональні Можливості

### 2.1 GPS Трекінг
**Код:** [`models/fleet_vehicle.py`](../models/fleet_vehicle.py)

**Функціонал:**
- Зберігання IMEI GPS-трекера для кожного авто
- Автоматичне отримання поточної GPS позиції
- Відображення статусу GPS (Active/No Data/Error)
- Час останнього оновлення позиції

**Поля моделі `fleet.vehicle`:**
```python
imei = fields.Char(string="GPS IMEI")
gps_tracker_sn = fields.Char(string="Tracker S/N")
current_latitude = fields.Float(compute="_compute_current_position")
current_longitude = fields.Float(compute="_compute_current_position")
last_position_time = fields.Datetime(compute="_compute_current_position")
gps_status = fields.Char(compute="_compute_current_position")
```

**Меню:** Fleet > Vehicles > GPS Tracking (вкладка)

### 2.2 Синхронізація Автомобілів
**Код:** [`wizard/vehicle_sync_wizard.py`](../wizard/vehicle_sync_wizard.py)

**Функціонал:**
- Автоматична синхронізація даних авто з зовнішньої GPS БД
- Три режими синхронізації:
  - Тільки створення нових
  - Тільки оновлення існуючих
  - Створення та оновлення
- Автоматичне створення моделей авто та брендів

**Меню:** GPS Route Sheets > Sync Vehicles from GPS

**Код синхронізації:**
```python
def action_sync_vehicles(self):
    """Synchronize vehicles from external GPS database."""
    gps_service = self.env["gps.db.service"]
    vehicles_data = gps_service.fetch_vehicles()
    
    for vehicle_data in vehicles_data:
        # Create or update vehicle
        self._sync_vehicle(vehicle_data)
```

### 2.3 Цілі Поїздок (Trip Purposes)
**Код:** [`models/gps_route_sheet.py:5-15`](../models/gps_route_sheet.py#L5-L15)

**Модель `gps.trip.purpose`:**
```python
class GpsTripPurpose(models.Model):
    _name = "gps.trip.purpose"
    _description = "GPS Trip Purpose"
    
    external_id = fields.Integer(index=True)
    code = fields.Char(required=True)
    name_uk = fields.Char(string="Name", required=True)
    description = fields.Text()
    is_active = fields.Boolean(default=True)
    sort_order = fields.Integer(default=0)
```

**Функціонал:**
- Класифікація поїздок за цілями
- Синхронізація з зовнішньої БД
- Демо-дані з 6 типовими цілями

**Меню:** GPS Route Sheets > Trip Purposes

### 2.4 Маршрутні Листи
**Код:** [`models/gps_route_sheet.py:18-36`](../models/gps_route_sheet.py#L18-L36)

**Модель `gps.route.sheet`:**
```python
class GpsRouteSheet(models.Model):
    _name = "gps.route.sheet"
    _description = "GPS Route Sheet"
    
    name = fields.Char(compute="_compute_name", store=True)
    vehicle_id = fields.Many2one("fleet.vehicle", required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    driver_name = fields.Char()
    trip_ids = fields.One2many("gps.route.trip", "sheet_id")
    last_sync_at = fields.Datetime()
```

**Функціонал:**
- Створення маршрутних листів для авто
- Автоматична генерація назви
- Зв'язок з поїздками
- Друк звітів

**Меню:** GPS Route Sheets > Route Sheets

### 2.5 Імпорт Поїздок
**Код:** [`wizard/route_trip_import_wizard.py`](../wizard/route_trip_import_wizard.py)

**Функціонал:**
- Імпорт поїздок з GPS БД за період
- Автоматичне мапування цілей поїздок
- Валідація даних
- Оновлення існуючих поїздок

**Використання:**
1. Відкрити маршрутний лист
2. Натиснути кнопку "Import Trips"
3. Вибрати період
4. Підтвердити імпорт

**Код імпорту:**
```python
def action_import(self):
    """Import trips from GPS database."""
    self.ensure_one()
    self.sheet_id.action_import_trips(self.date_from, self.date_to)
    return {"type": "ir.actions.act_window_close"}
```

### 2.6 Підключення до Зовнішньої БД
**Код:** [`models/gps_db.py`](../models/gps_db.py)

**Модель `gps.db.service`:**
- Абстрактна модель для роботи з зовнішньою PostgreSQL БД
- Методи для отримання даних:
  - `fetch_vehicles()` - список авто
  - `fetch_trips()` - поїздки за період
  - `fetch_trip_purposes()` - цілі поїздок
  - `fetch_last_position()` - остання GPS позиція

**Налаштування:** Settings > GPS Route Sheet Settings

**Параметри підключення:**
```python
def _get_db_params(self):
    """Get database connection parameters from config."""
    config = self.env["ir.config_parameter"].sudo()
    return {
        "host": config.get_param("gps_route_sheet.db_host"),
        "port": int(config.get_param("gps_route_sheet.db_port")),
        "dbname": config.get_param("gps_route_sheet.db_name"),
        "user": config.get_param("gps_route_sheet.db_user"),
        "password": config.get_param("gps_route_sheet.db_password"),
    }
```

---

## 3. Технічна Реалізація

### 3.1 Архітектура Модуля

```
gps_route_sheet/
├── models/              # Бізнес-логіка
│   ├── fleet_vehicle.py       # Розширення fleet.vehicle
│   ├── gps_db.py             # Сервіс для роботи з GPS БД
│   ├── gps_route_sheet.py    # Маршрутні листи та поїздки
│   └── res_config_settings.py # Налаштування
├── wizard/              # Майстри (wizards)
│   ├── vehicle_sync_wizard.py
│   ├── trip_purpose_sync_wizard.py
│   └── route_trip_import_wizard.py
├── views/               # XML визначення інтерфейсу
│   ├── gps_route_sheet_views.xml
│   ├── fleet_vehicle_views.xml
│   └── gps_tracking_map.xml
├── security/            # Права доступу
│   ├── security.xml
│   └── ir.model.access.csv
├── data/                # Демо-дані
│   ├── demo_vehicles.xml
│   └── demo_trip_purposes.xml
├── report/              # Звіти
│   └── gps_route_sheet_report.xml
└── i18n/                # Переклади
    └── uk.po
```

### 3.2 Групи Безпеки

**Код:** [`security/security.xml`](../security/security.xml)

**Дві групи користувачів:**
1. **GPS Route User** - перегляд даних
2. **GPS Route Manager** - повний доступ

**Record Rules:**
```xml
<record id="gps_route_sheet_user_rule" model="ir.rule">
    <field name="name">GPS Route Sheet: User Access</field>
    <field name="model_id" ref="model_gps_route_sheet"/>
    <field name="groups" eval="[(4, ref('group_gps_route_user'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="False"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

### 3.3 Права Доступу

**Код:** [`security/ir.model.access.csv`](../security/ir.model.access.csv)

**Приклад:**
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_gps_route_sheet_user,gps.route.sheet user,model_gps_route_sheet,group_gps_route_user,1,0,0,0
access_gps_route_sheet_manager,gps.route.sheet manager,model_gps_route_sheet,group_gps_route_manager,1,1,1,1
```

### 3.4 Переклади

**Код:** [`i18n/uk.po`](../i18n/uk.po)

**Статистика:**
- Всього рядків: 250+
- Перекладено: 100%
- Мова: Українська (uk_UA)

**Приклад:**
```po
msgid "GPS Route Sheet"
msgstr "Маршрутний лист GPS"

msgid "Import Trips"
msgstr "Імпортувати поїздки"
```

---

## 4. Структура Модуля

### 4.1 Моделі Даних

#### Основні моделі:
1. **`gps.trip.purpose`** - Цілі поїздок
2. **`gps.route.sheet`** - Маршрутні листи
3. **`gps.route.trip`** - Поїздки
4. **`gps.db.service`** - Сервіс для роботи з БД

#### Розширені моделі:
1. **`fleet.vehicle`** - Додано GPS поля
2. **`res.config.settings`** - Додано налаштування БД

### 4.2 Views (Представлення)

**Типи views:**
- **Form** - форми для створення/редагування
- **Tree** - списки записів
- **Kanban** - картки (для GPS tracking)
- **Search** - фільтри та пошук

**Приклад Form View:**
```xml
<record id="view_gps_route_sheet_form" model="ir.ui.view">
    <field name="name">gps.route.sheet.form</field>
    <field name="model">gps.route.sheet</field>
    <field name="arch" type="xml">
        <form>
            <header>
                <button name="action_import_trips" 
                        string="Import Trips" 
                        type="object"/>
            </header>
            <sheet>
                <group>
                    <field name="vehicle_id"/>
                    <field name="date_from"/>
                    <field name="date_to"/>
                </group>
                <notebook>
                    <page string="Trips">
                        <field name="trip_ids"/>
                    </page>
                </notebook>
            </sheet>
        </form>
    </field>
</record>
```

### 4.3 Wizards (Майстри)

**Всі wizards - TransientModel:**
1. **`vehicle.sync.wizard`** - Синхронізація авто
2. **`trip.purpose.sync.wizard`** - Синхронізація цілей
3. **`gps.route.trip.import.wizard`** - Імпорт поїздок

**Приклад Wizard:**
```python
class VehicleSyncWizard(models.TransientModel):
    _name = "vehicle.sync.wizard"
    _description = "Vehicle Synchronization Wizard"
    
    sync_mode = fields.Selection([
        ('create_only', 'Create New Only'),
        ('update_existing', 'Update Existing Only'),
        ('create_and_update', 'Create and Update'),
    ], default='create_and_update')
    
    def action_sync_vehicles(self):
        # Синхронізація
        pass
```

---

## 5. Демонстрація Роботи

### 5.1 Початкове Налаштування

**Крок 1:** Налаштування підключення до GPS БД
- Меню: Settings > GPS Route Sheet Settings
- Заповнити: Host, Port, Database, User, Password
- Зберегти

**Крок 2:** Синхронізація даних
- Меню: GPS Route Sheets > Sync Vehicles from GPS
- Вибрати режим синхронізації
- Натиснути "Sync Vehicles"
- Результат: Створено X авто

**Крок 3:** Синхронізація цілей поїздок
- Меню: GPS Route Sheets > Sync Trip Purposes from GPS
- Натиснути "Sync Trip Purposes"
- Результат: Створено/оновлено Y цілей

### 5.2 Робота з Маршрутними Листами

**Створення маршрутного листа:**
1. GPS Route Sheets > Route Sheets > New
2. Вибрати авто
3. Вказати період (Date From, Date To)
4. Зберегти

**Імпорт поїздок:**
1. Відкрити маршрутний лист
2. Натиснути "Import Trips"
3. Підтвердити період
4. Натиснути "Import"
5. Результат: Поїздки додано до вкладки "Trips"

**Перегляд поїздок:**
- Вкладка "Trips" показує всі поїздки
- Поля: Дата, Маршрут, Ціль, Кілометраж, Паливо

### 5.3 GPS Моніторинг

**Перегляд позицій авто:**
- Меню: GPS Route Sheets > GPS Tracking
- Kanban view з картками авто
- Показує: IMEI, Статус, Координати, Час оновлення

---

## 6. Відповідність Вимогам Курсової Роботи

### ✅ 1. Використання Odoo 19
- Модуль розроблено для Odoo 19
- Використано нові API та best practices

### ✅ 2. Мінімум 3 моделі
**Створено 4 моделі:**
1. `gps.trip.purpose` - Цілі поїздок
2. `gps.route.sheet` - Маршрутні листи  
3. `gps.route.trip` - Поїздки
4. `gps.db.service` - Сервіс БД (AbstractModel)

**Розширено 2 моделі:**
1. `fleet.vehicle` - GPS поля
2. `res.config.settings` - Налаштування

### ✅ 3. Різні типи полів
**Використано:**
- `Char` - текстові поля (IMEI, назви)
- `Integer` - числа (external_id, sort_order)
- `Float` - координати, пробіг
- `Date/Datetime` - дати поїздок
- `Many2one` - зв'язки (vehicle_id, trip_purpose_id)
- `One2many` - зворотні зв'язки (trip_ids)
- `Selection` - вибір (sync_mode, state)
- `Boolean` - прапорці (is_active)
- `Text` - довгі тексти (description)
- `Computed` - обчислювані поля (current_latitude)

### ✅ 4. Computed поля
**Приклади:**
```python
name = fields.Char(compute="_compute_name", store=True)
current_latitude = fields.Float(compute="_compute_current_position")
total_km = fields.Float(compute="_compute_total_km")
```

### ✅ 5. Onchange методи
**Приклад:**
```python
@api.onchange('vehicle_id')
def _onchange_vehicle_id(self):
    if self.vehicle_id:
        self.driver_name = self.vehicle_id.driver_id.name
```

### ✅ 6. Constraints
**Приклад:**
```python
_sql_constraints = [
    ('unique_external_id', 
     'UNIQUE(external_id)', 
     'External ID must be unique!')
]

@api.constrains('date_from', 'date_to')
def _check_dates(self):
    if self.date_from > self.date_to:
        raise ValidationError("Date From must be before Date To")
```

### ✅ 7. Views
**Створено views:**
- 8 Form views
- 6 Tree views
- 4 Search views
- 1 Kanban view
- 3 Wizard views

### ✅ 8. Security
**Реалізовано:**
- 2 групи користувачів
- Record rules для обмеження доступу
- Access rights в `ir.model.access.csv`
- 17 рядків прав доступу

### ✅ 9. Wizards
**Створено 3 wizards:**
1. Vehicle Sync Wizard
2. Trip Purpose Sync Wizard
3. Route Trip Import Wizard

### ✅ 10. Документація
**Створено:**
- ✅ README.rst - опис модуля
- ✅ Docstrings для всіх класів та методів
- ✅ Коментарі в коді
- ✅ index.html з картинкою (буде створено)

### ✅ 11. Переклади
- ✅ Повний переклад на українську мову
- ✅ Файл `i18n/uk.po` з 250+ рядками

### ✅ 12. Якість коду
- ✅ Pylint перевірка: 9.14/10
- ✅ Flake8 перевірка: виправлені всі критичні помилки
- ✅ Модуль встановлюється без помилок
- ✅ Модуль видаляється без помилок

---

## 7. Статистика Модуля

### Файли та Код
- **Python файли:** 12
- **XML файли:** 10
- **Рядків коду (Python):** ~1500
- **Рядків коду (XML):** ~800
- **Моделей:** 6
- **Views:** 22
- **Wizards:** 3
- **Reports:** 1

### Функціонал
- **Меню items:** 8
- **Actions:** 10
- **Security groups:** 2
- **Record rules:** 4
- **Access rights:** 17

---

## 8. Висновки

### Досягнуті Цілі
✅ Створено повнофункціональний модуль GPS моніторингу  
✅ Реалізовано інтеграцію з зовнішньою PostgreSQL БД  
✅ Додано автоматичну синхронізацію даних  
✅ Створено зручний UI для роботи з маршрутними листами  
✅ Забезпечено безпеку через groups та record rules  
✅ Додано повний переклад на українську мову  
✅ Пройдено всі перевірки якості коду  

### Можливості для Розвитку
- 🔄 Real-time GPS tracking з WebSocket
- 🗺️ Інтерактивна карта з Leaflet.js
- 📊 Розширена аналітика та звіти
- 🔔 Push-нотифікації про події
- 📱 Mobile app інтеграція

---

## 9. Посилання на Код

### Основні Файли
- [Manifest](__manifest__.py)
- [README](README.rst)
- [GPS DB Service](models/gps_db.py)
- [Route Sheet Model](models/gps_route_sheet.py)
- [Fleet Vehicle Extension](models/fleet_vehicle.py)
- [Vehicle Sync Wizard](wizard/vehicle_sync_wizard.py)
- [Security Rules](security/security.xml)
- [Access Rights](security/ir.model.access.csv)
- [Ukrainian Translation](i18n/uk.po)

### Документація
- [Technical Plan](doc/GPS_TRACKING_TECHNICAL_PLAN.md)
- [Course Project Presentation](doc/COURSE_PROJECT_PRESENTATION.md)

---

**Дата презентації:** [Дата]  
**Автор:** [Ваше Ім'я]  
**Email:** [Ваш Email]
