from odoo import _, fields, models
from odoo.exceptions import UserError


class GpsRouteTripImportWizard(models.TransientModel):
    _name = "gps.route.trip.import.wizard"
    _description = "GPS Route Trip Import Wizard"

    sheet_id = fields.Many2one("gps.route.sheet", required=True, readonly=True)
    vehicle_id = fields.Many2one("fleet.vehicle", required=True, readonly=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    def action_import(self):
        self.ensure_one()
        if not self.vehicle_id.imei:
            raise UserError(_("Vehicle IMEI is required to import trips."))
        self.sheet_id.action_import_trips(self.date_from, self.date_to)
        return {"type": "ir.actions.act_window_close"}
