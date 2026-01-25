from odoo import api, fields, models


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
        string="Fuel Card Number",
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
        string="Current Latitude",
        compute="_compute_current_position",
        store=False,
        digits=(10, 7),
    )
    current_longitude = fields.Float(
        string="Current Longitude",
        compute="_compute_current_position",
        store=False,
        digits=(10, 7),
    )
    last_position_time = fields.Datetime(
        string="Last Position Time",
        compute="_compute_current_position",
        store=False,
    )
    gps_status = fields.Char(
        string="GPS Status",
        compute="_compute_current_position",
        store=False,
    )

    @api.depends("imei")
    def _compute_current_position(self):
        """Compute current GPS position from external database."""
        for vehicle in self:
            if not vehicle.imei:
                vehicle.current_latitude = 0.0
                vehicle.current_longitude = 0.0
                vehicle.last_position_time = False
                vehicle.gps_status = "No IMEI"
                continue

            try:
                gps_service = self.env["gps.db.service"]
                position = gps_service.fetch_last_position(vehicle.imei)
                if position:
                    vehicle.current_latitude = position.get("latitude", 0.0)
                    vehicle.current_longitude = position.get("longitude", 0.0)
                    vehicle.last_position_time = position.get("timestamp")
                    vehicle.gps_status = "Active"
                else:
                    vehicle.current_latitude = 0.0
                    vehicle.current_longitude = 0.0
                    vehicle.last_position_time = False
                    vehicle.gps_status = "No Data"
            except Exception:
                vehicle.current_latitude = 0.0
                vehicle.current_longitude = 0.0
                vehicle.last_position_time = False
                vehicle.gps_status = "Error"
