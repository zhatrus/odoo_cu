from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    gps_db_host = fields.Char(config_parameter="gps_route_sheet.db_host")
    gps_db_port = fields.Integer(config_parameter="gps_route_sheet.db_port", default=5432)
    gps_db_name = fields.Char(config_parameter="gps_route_sheet.db_name")
    gps_db_user = fields.Char(config_parameter="gps_route_sheet.db_user")
    gps_db_password = fields.Char(config_parameter="gps_route_sheet.db_password")
