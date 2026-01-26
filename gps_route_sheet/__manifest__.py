{
    "name": "GPS Fleet Management",
    "summary": "GPS tracking, route sheets, and fuel management for "
    "fleet vehicles",
    "version": "19.0.1.0.0",
    "category": "Fleet/Management",
    "license": "LGPL-3",
    "author": "zhatrus",
    "website": "https://github.com/zhatrus",
    "depends": ["fleet", "base"],
    "external_dependencies": {
        "python": ["psycopg2"],
    },
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/gps_route_sheet_views.xml",
        "views/fleet_vehicle_views.xml",
        "views/res_config_settings_views.xml",
        "views/gps_tracking_map.xml",
        # "views/gps_dashboard.xml",  # Temporarily disabled for testing
        "wizard/vehicle_sync_wizard_views.xml",
        "wizard/trip_purpose_sync_wizard_views.xml",
        "views/route_trip_import_wizard_views.xml",
        "report/gps_route_sheet_report.xml",
    ],
    "demo": [
        "data/demo_vehicles.xml",
        "data/demo_trip_purposes.xml",
    ],
    "images": [
        "static/description/icon.png",
        "static/description/banner.png",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
