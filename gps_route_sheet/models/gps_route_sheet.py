from odoo import api, fields, models


class GpsTripPurpose(models.Model):
    _name = "gps.trip.purpose"
    _description = "GPS Trip Purpose"
    _order = "sort_order, name_uk"

    code = fields.Char(required=True)
    name_uk = fields.Char(string="Name", required=True)
    description = fields.Text()
    is_active = fields.Boolean(default=True)
    sort_order = fields.Integer(default=0)


class GpsRouteSheet(models.Model):
    _name = "gps.route.sheet"
    _description = "GPS Route Sheet"

    name = fields.Char(default="/", required=True)
    vehicle_id = fields.Many2one("fleet.vehicle", required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    driver_name = fields.Char()
    trip_ids = fields.One2many("gps.route.trip", "sheet_id")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.name == "/":
                record.name = f"RS/{record.vehicle_id.display_name}/{record.date_from}"
        return records


class GpsRouteTrip(models.Model):
    _name = "gps.route.trip"
    _description = "GPS Route Trip"
    _order = "trip_date, id"

    sheet_id = fields.Many2one("gps.route.sheet", ondelete="cascade")
    external_trip_id = fields.Integer(index=True)
    trip_date = fields.Date(required=True)
    route_description = fields.Text()
    trip_purpose_id = fields.Many2one("gps.trip.purpose")
    trip_purpose_other = fields.Text()
    in_city_km = fields.Integer(default=0)
    outside_city_km = fields.Integer(default=0)
    total_km = fields.Integer(default=0)
    city_coefficient = fields.Float(default=1.0, digits=(3, 2))
    outside_coefficient = fields.Float(default=1.0, digits=(3, 2))
    fuel_liters = fields.Float(digits=(10, 2))
    project_name = fields.Char()
    payment_type = fields.Char()
    driver_name = fields.Char()
    user_comment = fields.Text()
    state = fields.Selection(
        [("active", "Active"), ("skipped", "Skipped"), ("deleted", "Deleted")],
        default="active",
        required=True,
    )
