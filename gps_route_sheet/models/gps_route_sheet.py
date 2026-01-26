from odoo import _, api, fields, models
from odoo.exceptions import UserError


class GpsTripPurpose(models.Model):
    _name = "gps.trip.purpose"
    _description = "GPS Trip Purpose"
    _order = "sort_order, name_uk"

    external_id = fields.Integer(index=True)
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
    last_sync_at = fields.Datetime(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.name == "/":
                record.name = (
                    f"RS/{record.vehicle_id.display_name}/"
                    f"{record.date_from}"
                )
        return records

    def action_import_trips(self, date_from=None, date_to=None):  # pylint: disable=too-many-locals
        for sheet in self:
            if not sheet.vehicle_id.imei:
                raise UserError(_("Vehicle IMEI is required to import trips."))
            start = date_from or sheet.date_from
            end = date_to or sheet.date_to
            rows = self.env["gps.db.service"].fetch_trips(
                sheet.vehicle_id.imei,
                start,
                end,
            )
            trips = []
            purpose_map = {
                purpose.external_id: purpose.id
                for purpose in self.env["gps.trip.purpose"].search([])
                if purpose.external_id
            }
            existing = {
                trip.external_trip_id
                for trip in sheet.trip_ids
                if trip.external_trip_id
            }
            for row in rows:
                (
                    trip_id,
                    trip_date,
                    route_description,
                    trip_purpose_id,
                    trip_purpose_other,
                    in_city_km,
                    outside_city_km,
                    total_km,
                    city_coefficient,
                    outside_coefficient,
                    fuel_liters,
                    project_name,
                    payment_type,
                    driver_name,
                    user_comment,
                ) = row
                if trip_id in existing:
                    continue
                trips.append(
                    {
                        "sheet_id": sheet.id,
                        "external_trip_id": trip_id,
                        "trip_date": trip_date,
                        "route_description": route_description,
                        "trip_purpose_id": purpose_map.get(trip_purpose_id),
                        "trip_purpose_other": trip_purpose_other,
                        "in_city_km": in_city_km or 0,
                        "outside_city_km": outside_city_km or 0,
                        "total_km": total_km or 0,
                        "city_coefficient": city_coefficient or 1.0,
                        "outside_coefficient": outside_coefficient or 1.0,
                        "fuel_liters": fuel_liters,
                        "project_name": project_name,
                        "payment_type": payment_type,
                        "driver_name": driver_name,
                        "user_comment": user_comment,
                    }
                )
            if trips:
                self.env["gps.route.trip"].create(trips)
            sheet.last_sync_at = fields.Datetime.now()

    def action_sync_trip_purposes(self):
        rows = self.env["gps.db.service"].fetch_trip_purposes()
        existing = {
            purpose.external_id: purpose
            for purpose in self.env["gps.trip.purpose"].search([])
            if purpose.external_id
        }
        for row in rows:
            (
                external_id,
                code,
                name_uk,
                description,
                is_active,
                sort_order,
            ) = row
            if external_id in existing:
                existing[external_id].write(
                    {
                        "code": code,
                        "name_uk": name_uk,
                        "description": description,
                        "is_active": is_active,
                        "sort_order": sort_order,
                    }
                )
            else:
                self.env["gps.trip.purpose"].create(
                    {
                        "external_id": external_id,
                        "code": code,
                        "name_uk": name_uk,
                        "description": description,
                        "is_active": is_active,
                        "sort_order": sort_order,
                    }
                )

    def action_open_import_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Import Trips",
            "res_model": "gps.route.trip.import.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_sheet_id": self.id,
                "default_date_from": self.date_from,
                "default_date_to": self.date_to,
                "default_vehicle_id": self.vehicle_id.id,
            },
        }


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
