# GPS Fleet Tracking - Детальний Технічний План

## 1. Огляд Системи

### 1.1 Архітектура
```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Odoo Backend  │◄────►│  GPS Tracking    │◄────►│  External GPS   │
│   (Python)      │      │  Controller      │      │  Database       │
└────────┬────────┘      └──────────────────┘      └─────────────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│   Web Frontend  │◄────►│  Leaflet.js Map  │
│   (QWeb/JS)     │      │  + OpenStreetMap │
└─────────────────┘      └──────────────────┘
```

### 1.2 Технологічний Стек
- **Backend**: Odoo 19, Python 3.10+, PostgreSQL
- **Frontend**: QWeb Templates, JavaScript ES6+, Bootstrap 5
- **Mapping**: Leaflet.js 1.9.4, OpenStreetMap Tiles
- **Data Source**: External PostgreSQL DB (GPS tracker data)
- **API**: Odoo JSON-RPC, RESTful endpoints

## 2. Варіанти Реалізації GPS Моніторингу

### Варіант A: Iframe з Зовнішнім Сервісом (Рекомендовано)

**Переваги:**
- Швидка реалізація (1-2 дні)
- Не потребує модуля `website`
- Використання готових картографічних сервісів
- Легке обслуговування

**Недоліки:**
- Залежність від зовнішніх сервісів
- Обмежені можливості кастомізації

**Технічна Реалізація:**

#### 2.1 Створення Standalone HTML Application

```html
<!-- static/src/html/gps_map.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>GPS Fleet Tracking</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body { margin: 0; padding: 0; }
        #map { height: 100vh; width: 100%; }
        .vehicle-panel {
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 1000;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            max-height: 90vh;
            overflow-y: auto;
            width: 320px;
        }
        .vehicle-item {
            padding: 10px;
            margin: 5px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .vehicle-item:hover {
            background-color: #f0f0f0;
            transform: translateX(5px);
        }
        .vehicle-item.active {
            background-color: #e3f2fd;
            border-color: #2196F3;
        }
        .info-panel {
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1000;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            width: 350px;
            display: none;
        }
        .info-panel.show { display: block; }
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .info-label { font-weight: 600; color: #666; }
        .info-value { color: #333; }
        .status-online { color: #4CAF50; }
        .status-offline { color: #F44336; }
    </style>
</head>
<body>
    <div class="vehicle-panel">
        <h3>Vehicles</h3>
        <div id="vehicleList"></div>
    </div>
    
    <div class="info-panel" id="infoPanel">
        <h4 id="vehicleName"></h4>
        <div id="vehicleDetails"></div>
    </div>
    
    <div id="map"></div>
    
    <script>
        // Configuration
        const ODOO_URL = window.location.origin;
        const API_ENDPOINT = '/gps/tracking/vehicles';
        const REFRESH_INTERVAL = 30000; // 30 seconds
        
        let map, markers = {};
        let selectedVehicleId = null;
        
        // Initialize map
        function initMap() {
            map = L.map('map').setView([50.4501, 30.5234], 6);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 18,
            }).addTo(map);
        }
        
        // Fetch vehicles from Odoo
        async function fetchVehicles() {
            try {
                const response = await fetch(ODOO_URL + '/web/dataset/call_kw', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: {
                            model: 'fleet.vehicle',
                            method: 'search_read',
                            args: [[['imei', '!=', false]]],
                            kwargs: {
                                fields: ['id', 'license_plate', 'imei', 
                                        'current_latitude', 'current_longitude',
                                        'last_position_time', 'gps_status']
                            }
                        },
                        id: Math.floor(Math.random() * 1000)
                    })
                });
                
                const data = await response.json();
                return data.result || [];
            } catch (error) {
                console.error('Error fetching vehicles:', error);
                return [];
            }
        }
        
        // Update map with vehicles
        async function updateMap() {
            const vehicles = await fetchVehicles();
            const listContainer = document.getElementById('vehicleList');
            listContainer.innerHTML = '';
            
            // Clear existing markers
            Object.values(markers).forEach(marker => map.removeLayer(marker));
            markers = {};
            
            vehicles.forEach(vehicle => {
                if (vehicle.current_latitude && vehicle.current_longitude) {
                    // Add to list
                    const item = document.createElement('div');
                    item.className = 'vehicle-item';
                    item.innerHTML = `
                        <strong>${vehicle.license_plate}</strong><br>
                        <small>IMEI: ${vehicle.imei}</small><br>
                        <small class="status-${vehicle.gps_status === 'Active' ? 'online' : 'offline'}">
                            ${vehicle.gps_status}
                        </small>
                    `;
                    item.onclick = () => selectVehicle(vehicle);
                    listContainer.appendChild(item);
                    
                    // Add marker
                    const marker = L.marker([
                        vehicle.current_latitude,
                        vehicle.current_longitude
                    ]).addTo(map);
                    
                    marker.bindPopup(`
                        <b>${vehicle.license_plate}</b><br>
                        IMEI: ${vehicle.imei}<br>
                        Status: ${vehicle.gps_status}
                    `);
                    
                    marker.on('click', () => selectVehicle(vehicle));
                    markers[vehicle.id] = marker;
                }
            });
            
            // Fit map to markers
            if (Object.keys(markers).length > 0) {
                const group = L.featureGroup(Object.values(markers));
                map.fitBounds(group.getBounds().pad(0.1));
            }
        }
        
        // Select vehicle and show details
        function selectVehicle(vehicle) {
            selectedVehicleId = vehicle.id;
            
            // Update list selection
            document.querySelectorAll('.vehicle-item').forEach(item => {
                item.classList.remove('active');
            });
            event.currentTarget.classList.add('active');
            
            // Show info panel
            const infoPanel = document.getElementById('infoPanel');
            const vehicleName = document.getElementById('vehicleName');
            const vehicleDetails = document.getElementById('vehicleDetails');
            
            vehicleName.textContent = vehicle.license_plate;
            
            vehicleDetails.innerHTML = `
                <div class="info-row">
                    <span class="info-label">IMEI:</span>
                    <span class="info-value">${vehicle.imei}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Latitude:</span>
                    <span class="info-value">${vehicle.current_latitude.toFixed(6)}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Longitude:</span>
                    <span class="info-value">${vehicle.current_longitude.toFixed(6)}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Last Update:</span>
                    <span class="info-value">${new Date(vehicle.last_position_time).toLocaleString('uk-UA')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Status:</span>
                    <span class="info-value status-${vehicle.gps_status === 'Active' ? 'online' : 'offline'}">
                        ${vehicle.gps_status}
                    </span>
                </div>
            `;
            
            infoPanel.classList.add('show');
            
            // Center map on vehicle
            if (markers[vehicle.id]) {
                map.setView([vehicle.current_latitude, vehicle.current_longitude], 15);
                markers[vehicle.id].openPopup();
            }
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            initMap();
            updateMap();
            setInterval(updateMap, REFRESH_INTERVAL);
        });
    </script>
</body>
</html>
```

#### 2.2 Інтеграція в Odoo через Iframe

```xml
<!-- views/gps_tracking_iframe.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_gps_tracking_iframe" model="ir.ui.view">
        <field name="name">gps.tracking.iframe</field>
        <field name="model">fleet.vehicle</field>
        <field name="arch" type="xml">
            <form string="GPS Tracking Map">
                <sheet>
                    <div class="oe_title">
                        <h1>GPS Fleet Tracking</h1>
                    </div>
                    <group>
                        <iframe 
                            src="/gps_route_sheet/static/src/html/gps_map.html"
                            style="width:100%; height:800px; border:none;"
                            sandbox="allow-scripts allow-same-origin">
                        </iframe>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_gps_tracking_iframe" model="ir.actions.act_window">
        <field name="name">GPS Tracking Map</field>
        <field name="res_model">fleet.vehicle</field>
        <field name="view_mode">form</field>
        <field name="view_id" ref="view_gps_tracking_iframe"/>
        <field name="target">fullscreen</field>
    </record>

    <menuitem
        id="menu_gps_tracking_map"
        name="GPS Tracking Map"
        parent="menu_gps_root"
        action="action_gps_tracking_iframe"
        sequence="1"/>
</odoo>
```

### Варіант B: Odoo JS Widget (Складніше, але інтегрованіше)

**Переваги:**
- Повна інтеграція з Odoo UI
- Доступ до Odoo RPC
- Кращий UX

**Недоліки:**
- Складніша реалізація (3-5 днів)
- Потребує знання Odoo JS framework

**Структура:**
```
static/src/
├── js/
│   ├── gps_map_widget.js
│   └── gps_map_controller.js
├── xml/
│   └── gps_map_templates.xml
└── scss/
    └── gps_map.scss
```

### Варіант C: Використання Google Maps API

**API Key Required**: Потрібен API ключ Google Maps

**Приклад інтеграції:**
```javascript
function initGoogleMap() {
    const map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 50.4501, lng: 30.5234 },
        zoom: 6
    });
    
    // Add markers for each vehicle
    vehicles.forEach(vehicle => {
        new google.maps.Marker({
            position: { 
                lat: vehicle.current_latitude, 
                lng: vehicle.current_longitude 
            },
            map: map,
            title: vehicle.license_plate
        });
    });
}
```

## 3. Додаткові Функції

### 3.1 Reverse Geocoding (Отримання Адреси)

**Використання Nominatim API (OpenStreetMap):**
```javascript
async function getAddress(lat, lon) {
    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`;
    const response = await fetch(url);
    const data = await response.json();
    return data.display_name;
}
```

### 3.2 Real-time Updates (WebSocket)

**Опціонально**: Використання Odoo Longpolling або WebSocket для real-time оновлень

### 3.3 Історія Маршрутів

**Відображення треку руху:**
```javascript
const polyline = L.polyline(coordinates, {color: 'blue'}).addTo(map);
map.fitBounds(polyline.getBounds());
```

## 4. План Імплементації (Варіант A - Рекомендовано)

### День 1: Базова Структура
- [x] Створити HTML файл з Leaflet картою
- [x] Додати базові стилі
- [x] Інтегрувати OpenStreetMap tiles

### День 2: Інтеграція з Odoo
- [ ] Створити iframe view в Odoo
- [ ] Налаштувати API endpoints
- [ ] Додати menu item

### День 3: Функціонал
- [ ] Відображення маркерів авто
- [ ] Панель списку авто
- [ ] Панель деталей авто
- [ ] Auto-refresh

### День 4: Покращення
- [ ] Додати reverse geocoding
- [ ] Покращити UI/UX
- [ ] Додати фільтри та пошук

### День 5: Тестування
- [ ] Тестування на різних браузерах
- [ ] Оптимізація продуктивності
- [ ] Документація

## 5. Альтернативні Рішення

### Self-hosted Tile Server
**Для повної незалежності:**
- OpenStreetMap Tile Server
- Docker container з tiles
- Nginx для кешування

### Комерційні Сервіси
- **Mapbox**: $5/місяць, 50k запитів
- **Google Maps**: Pay-as-you-go
- **HERE Maps**: Безкоштовно до 250k запитів/місяць

## 6. Безпека та Продуктивність

### 6.1 Безпека
- CORS налаштування
- Rate limiting для API
- Валідація GPS координат

### 6.2 Оптимізація
- Кешування tile
- Lazy loading маркерів
- Clustering для великої кількості авто

## 7. Висновок

**Рекомендація**: Варіант A (Iframe + Standalone HTML)
- Швидка реалізація
- Легке обслуговування
- Не потребує додаткових залежностей
- Працює без модуля `website`

**Наступні кроки**:
1. Створити HTML файл
2. Додати iframe view
3. Протестувати
4. Додати до презентації курсової роботи
