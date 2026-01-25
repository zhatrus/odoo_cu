from odoo import fields, models


class GpsRouteTripImportWizard(models.TransientModel):
    _name = "gps.route.trip.import.wizard"
    _description = "Import Trips from GPS Database"

    sheet_id = fields.Many2one("gps.route.sheet", required=True, readonly=True)
    vehicle_id = fields.Many2one(
        "fleet.vehicle", related="sheet_id.vehicle_id", readonly=True
    )
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    def action_import(self):
        self.ensure_one()
        self.sheet_id.action_import_trips(self.date_from, self.date_to)
        return {"type": "ir.actions.act_window_close"}
