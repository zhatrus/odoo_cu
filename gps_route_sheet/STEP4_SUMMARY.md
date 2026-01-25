# Крок 4: Демо дані + переклад UK + pylint

## Що зроблено:

### 1. ✅ Демо дані (`data/demo_vehicles.xml`):
- **3 виробники:** Ford, Toyota, Volkswagen
- **3 моделі:** Ford/Focus, Toyota/Camry, Volkswagen/Passat
- **3 транспортні засоби** з повними GPS даними:
  - AA1234BB - Ford Focus (IMEI: 350317172983730)
  - BC5678DE - Toyota Camry (IMEI: 350317172983731)
  - EF9012GH - VW Passat (IMEI: 350317172983732)
- Кожен має: IMEI, GPS S/N, паливну картку, норму витрат, SIM, псевдонім

### 2. ✅ Український переклад (`i18n/uk.po`):
- Всі поля моделі fleet.vehicle
- Wizard синхронізації
- Views та меню
- Повідомлення про помилки
- **Загалом ~40 перекладів**

### 3. ✅ Оновлено `__manifest__.py`:
- Додано demo секцію з `data/demo_vehicles.xml`

## Команди для тестування:

```bash
cd /home/mini/odoo/odoo19/repositories/odoo_cu
git pull

# Видалити та переінсталювати з demo даними
odoo-helper stop
/home/mini/odoo/odoo19/venv/bin/odoo -c /home/mini/odoo/odoo19/conf/odoo.conf -d odoo19 --uninstall gps_route_sheet --stop-after-init
/home/mini/odoo/odoo19/venv/bin/odoo -c /home/mini/odoo/odoo19/conf/odoo.conf -i gps_route_sheet -d odoo19 --stop-after-init --load-language=uk_UA
odoo-helper start
```

## Перевірка в UI:

1. **Fleet → Vehicles** - має бути 3 демо авто
2. Відкрити будь-яке авто → вкладка **GPS Tracking**
3. Всі поля мають бути заповнені
4. Перевірити переклад (якщо мова UK)

## Pylint/Flake8:

Запустити на VM:
```bash
cd /home/mini/odoo/odoo19/repositories/odoo_cu/gps_route_sheet
pylint models/fleet_vehicle.py wizard/vehicle_sync_wizard.py --disable=C0114,C0115,C0116,R0903
```

## Наступний крок:
**Крок 5:** Модель gps.trip.purpose з синхронізацією
