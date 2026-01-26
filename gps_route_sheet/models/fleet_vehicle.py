import logging

from odoo import api, fields, models


_logger = logging.getLogger(__name__)


class FleetVehicle(models.Model):
    """Extend fleet.vehicle with GPS tracking capabilities."""

    _inherit = "fleet.vehicle"

    imei = fields.Char(
        string="GPS IMEI",
        size=20,
        help="IMEI number of the GPS tracker device",
    )
    gps_tracker_sn = fields.Char(
        string="Tracker S/N",
        size=20,
        help="Serial number of GPS tracker",
    )
    fuel_card_number = fields.Char(
        size=20,
        help="Fuel card number for transaction tracking",
    )
    fuel_norm_l_100km = fields.Float(
        string="Fuel Norm (L/100km)",
        digits=(5, 2),
        help="Standard fuel consumption per 100 km",
    )
    sim_number = fields.Char(
        string="SIM Number",
        size=20,
        help="SIM card number in GPS tracker",
    )
    gps_alias = fields.Char(
        string="GPS Alias",
        help="Alternative name for GPS tracking system",
    )

    current_latitude = fields.Float(
        compute="_compute_current_position",
        store=False,
        digits=(10, 7),
    )
    current_longitude = fields.Float(
        compute="_compute_current_position",
        store=False,
        digits=(10, 7),
    )
    last_position_time = fields.Datetime(
        compute="_compute_current_position",
        store=False,
    )
    gps_status = fields.Char(
        string="GPS Status",
        compute="_compute_current_position",
        store=False,
    )
    current_speed = fields.Float(
        string="Current Speed (km/h)",
        compute="_compute_current_position",
        store=False,
        digits=(5, 1),
        help="Current speed from GPS tracker",
    )
    current_satellites = fields.Integer(
        string="GPS Satellites",
        compute="_compute_current_position",
        store=False,
        help="Number of GPS satellites in view",
    )
    current_angle = fields.Float(
        string="Direction (degrees)",
        compute="_compute_current_position",
        store=False,
        digits=(5, 1),
        help="Direction of movement in degrees (0-360)",
    )
    current_odometer = fields.Integer(
        string="GPS Odometer (km)",
        compute="_compute_current_position",
        store=False,
        help="Current odometer reading from GPS tracker",
    )
    current_ignition = fields.Boolean(
        string="Ignition Status",
        compute="_compute_current_position",
        store=False,
        help="Engine ignition status from GPS",
    )
    current_fuel_level = fields.Float(
        string="Fuel Level (%)",
        compute="_compute_current_position",
        store=False,
        digits=(5, 1),
        help="Current fuel level percentage from GPS",
    )
    current_battery = fields.Float(
        string="Vehicle Battery (V)",
        compute="_compute_current_position",
        store=False,
        digits=(4, 2),
        help="Vehicle battery voltage",
    )
    current_device_battery = fields.Float(
        string="GPS Device Battery (V)",
        compute="_compute_current_position",
        store=False,
        digits=(4, 2),
        help="GPS tracker device battery voltage",
    )
    last_fuel_date = fields.Datetime(
        string="Last Refueling Date",
        compute="_compute_last_fuel_transaction",
        store=False,
        help="Date and time of last fuel transaction",
    )
    last_fuel_volume = fields.Float(
        string="Last Refueling Volume (L)",
        compute="_compute_last_fuel_transaction",
        store=False,
        digits=(6, 2),
        help="Volume of last fuel transaction in liters",
    )
    last_fuel_amount = fields.Float(
        string="Last Refueling Amount",
        compute="_compute_last_fuel_transaction",
        store=False,
        digits=(10, 2),
        help="Amount of last fuel transaction",
    )

    @api.depends("imei")
    # pylint: disable=too-many-statements
    def _compute_current_position(self):
        """Compute current GPS position from external database."""
        for vehicle in self:
            if not vehicle.imei:
                vehicle.current_latitude = 0.0
                vehicle.current_longitude = 0.0
                vehicle.last_position_time = False
                vehicle.gps_status = "No IMEI"
                vehicle.current_speed = 0.0
                vehicle.current_satellites = 0
                vehicle.current_angle = 0.0
                vehicle.current_odometer = 0.0
                vehicle.current_ignition = False
                vehicle.current_fuel_level = 0.0
                vehicle.current_battery = 0.0
                vehicle.current_device_battery = 0.0
                continue

            try:
                gps_service = self.env["gps.db.service"]
                position = gps_service.fetch_last_position(vehicle.imei)
                if position:
                    vehicle.current_latitude = position.get("latitude", 0.0)
                    vehicle.current_longitude = position.get("longitude", 0.0)
                    vehicle.last_position_time = position.get("timestamp")
                    vehicle.current_speed = position.get("speed", 0.0)
                    vehicle.current_satellites = position.get("satellites", 0)
                    vehicle.current_angle = position.get("angle", 0.0)
                    vehicle.current_odometer = position.get("odometer", 0.0)
                    vehicle.current_ignition = position.get("ignition", False)
                    vehicle.current_fuel_level = position.get("fuel", 0.0)
                    vehicle.current_battery = position.get("battery", 0.0)
                    vehicle.current_device_battery = position.get(
                        "device_battery", 0.0
                    )
                    vehicle.gps_status = "Active"
                else:
                    vehicle.current_latitude = 0.0
                    vehicle.current_longitude = 0.0
                    vehicle.last_position_time = False
                    vehicle.gps_status = "No Data"
                    vehicle.current_speed = 0.0
                    vehicle.current_satellites = 0
                    vehicle.current_angle = 0.0
                    vehicle.current_odometer = 0.0
                    vehicle.current_ignition = False
                    vehicle.current_fuel_level = 0.0
                    vehicle.current_battery = 0.0
                    vehicle.current_device_battery = 0.0
            except (KeyError, TypeError, ValueError, ConnectionError):
                vehicle.current_latitude = 0.0
                vehicle.current_longitude = 0.0
                vehicle.last_position_time = False
                vehicle.gps_status = "Error"
                vehicle.current_speed = 0.0
                vehicle.current_satellites = 0
                vehicle.current_angle = 0.0
                vehicle.current_odometer = 0.0
                vehicle.current_ignition = False
                vehicle.current_fuel_level = 0.0
                vehicle.current_battery = 0.0
                vehicle.current_device_battery = 0.0

    @api.depends("fuel_card_number")
    def _compute_last_fuel_transaction(self):
        """Compute last fuel transaction from GPS database."""
        for vehicle in self:
            if not vehicle.fuel_card_number:
                vehicle.last_fuel_date = False
                vehicle.last_fuel_volume = 0.0
                vehicle.last_fuel_amount = 0.0
                continue

            try:
                gps_service = self.env["gps.db.service"]
                transaction = gps_service.fetch_last_fuel_transaction(
                    vehicle.fuel_card_number
                )
                if transaction:
                    vehicle.last_fuel_date = transaction.get("trans_date")
                    vehicle.last_fuel_volume = transaction.get("volume", 0.0)
                    vehicle.last_fuel_amount = transaction.get("amount", 0.0)
                else:
                    vehicle.last_fuel_date = False
                    vehicle.last_fuel_volume = 0.0
                    vehicle.last_fuel_amount = 0.0
            except (KeyError, TypeError, ValueError, ConnectionError):
                vehicle.last_fuel_date = False
                vehicle.last_fuel_volume = 0.0
                vehicle.last_fuel_amount = 0.0

    def action_sync_odometer(self):
        """Sync odometer value from GPS tracker to Odoo."""
        for vehicle in self:
            if not vehicle.imei:
                continue
            try:
                gps_service = self.env["gps.db.service"]
                position = gps_service.fetch_last_position(vehicle.imei)
                if position and position.get("odometer"):
                    odometer_km = position.get("odometer", 0.0)
                    if odometer_km > 0:
                        vehicle.odometer = int(odometer_km)
            except (KeyError, TypeError, ValueError, ConnectionError) as exc:
                _logger.warning(
                    "Failed to sync odometer from GPS for vehicle %s: %s",
                    vehicle.display_name,
                    exc,
                )

    def action_sync_all_odometers(self):
        """Sync odometers for all vehicles with GPS."""
        vehicles = self.search([("imei", "!=", False)])
        vehicles.action_sync_odometer()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Odometer Sync",
                "message": f"Synced odometers for {len(vehicles)} vehicles",
                "type": "success",
            },
        }

    def action_open_google_maps(self):
        """Open Google Maps with current GPS coordinates."""
        self.ensure_one()
        if not self.current_latitude or not self.current_longitude:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "No GPS Data",
                    "message": "No GPS coordinates available for this vehicle",
                    "type": "warning",
                },
            }
        url = (
            f"https://www.google.com/maps/search/?api=1&"
            f"query={self.current_latitude},{self.current_longitude}"
        )
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }
