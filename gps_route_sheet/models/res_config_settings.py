from odoo import api, fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    gps_db_host = fields.Char(config_parameter="gps_route_sheet.db_host")
    gps_db_port = fields.Char(config_parameter="gps_route_sheet.db_port", default="5432")
    gps_db_name = fields.Char(config_parameter="gps_route_sheet.db_name")
    gps_db_user = fields.Char(config_parameter="gps_route_sheet.db_user")
    gps_db_password = fields.Char(config_parameter="gps_route_sheet.db_password")

    @api.model
    def action_test_gps_db_connection(self, *args, **kwargs):
        self.ensure_one()
        try:
            self.env["gps.db.service"].test_connection()
        except UserError:
            raise
        except Exception as exc:
            raise UserError(f"GPS database connection failed: {exc}") from exc
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "GPS Route Sheet",
                "message": "Connection successful.",
                "type": "success",
                "sticky": False,
            },
        }
