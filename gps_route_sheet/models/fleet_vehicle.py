from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    imei = fields.Char(string="GPS IMEI", size=20)
