{
    "name": "GPS Fleet Management",
    "summary": "GPS tracking, route sheets, and fuel management for fleet vehicles",
    "description": """
        GPS Fleet Management
        ====================
        
        Comprehensive GPS tracking and fleet management solution for organizations 
        with vehicle fleets equipped with GPS trackers.
        
        Key Features:
        -------------
        * **Real-time GPS Tracking**: Monitor vehicle locations with IMEI-based integration
        * **Automatic Trip Synchronization**: Configurable auto-sync from PostgreSQL database
        * **Route Sheet Management**: Generate and print official route sheets
        * **Fuel Transaction Tracking**: Monitor fuel consumption and analyze vs norms
        * **Speed Violation Monitoring**: Automatic detection and alerts
        * **Advanced Analytics**: Pivot tables and graphs for comprehensive analysis
        * **Multi-level Access Control**: User and Manager roles with record rules
        
        Technical Features:
        ------------------
        * PostgreSQL external database connector for GPS data
        * Automated synchronization (trips every 5 min, fuel hourly - configurable)
        * Trip purpose classification system
        * Integration with standard Odoo Fleet module
        * Comprehensive demo data and Ukrainian translation included
        * QWeb printable reports
        
        Perfect for NGOs, delivery services, and any organization managing vehicle fleets.
    """,
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
