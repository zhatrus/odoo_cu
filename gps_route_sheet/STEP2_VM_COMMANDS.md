# Команди для оновлення модуля на VM (Odoo 19)

## Після git pull виконати:

```bash
cd /home/mini/odoo/odoo19/repositories/odoo_cu

# 1. Оновити список модулів
odoo-helper addons update-list

# 2. Оновити модуль через odoo-bin
odoo-helper stop
/home/mini/odoo/odoo19/venv/bin/odoo -c /home/mini/odoo/odoo19/conf.d/odoo.conf -u gps_route_sheet -d odoo19 --stop-after-init

# 3. Запустити сервер
odoo-helper start

# Або все разом:
odoo-helper restart --update gps_route_sheet
```

## Якщо помилка "role mini does not exist":

```bash
# Перевірити конфігурацію БД
cat /home/mini/odoo/odoo19/conf.d/odoo.conf | grep db_

# Або використати правильну команду odoo-helper
odoo-helper db upgrade gps_route_sheet
```

## Перевірка після оновлення:

```bash
# Перевірити логи
odoo-helper server log

# Або tail логів
tail -f /home/mini/odoo/odoo19/logs/odoo.log
```

## Доступ до Odoo:
http://localhost:15069/

Логін: admin (або ваш користувач)
