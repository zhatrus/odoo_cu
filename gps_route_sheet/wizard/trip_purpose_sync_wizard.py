from odoo import fields, models


class TripPurposeSyncWizard(models.TransientModel):
    _name = "trip.purpose.sync.wizard"
    _description = "Sync Trip Purposes from GPS Database"

    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")],
        default="draft",
        readonly=True,
    )
    purpose_count = fields.Integer(readonly=True)
    result_message = fields.Text(readonly=True)

    def action_sync_purposes(self):
        """Synchronize trip purposes from GPS database."""
        self.ensure_one()
        try:
            rows = self.env["gps.db.service"].fetch_trip_purposes()
            existing = {
                p.external_id: p
                for p in self.env["gps.trip.purpose"].search([])
                if p.external_id
            }
            created = 0
            updated = 0
            for row in rows:
                (
                    external_id,
                    code,
                    name_uk,
                    description,
                    is_active,
                    sort_order,
                ) = row
                vals = {
                    "code": code,
                    "name_uk": name_uk,
                    "description": description,
                    "is_active": is_active,
                    "sort_order": sort_order or 0,
                }
                if external_id in existing:
                    existing[external_id].write(vals)
                    updated += 1
                else:
                    vals["external_id"] = external_id
                    self.env["gps.trip.purpose"].create(vals)
                    created += 1

            self.write({
                "state": "done",
                "purpose_count": created + updated,
                "result_message": f"Created: {created}, Updated: {updated}",
            })
        except Exception as e:
            self.write({
                "state": "done",
                "purpose_count": 0,
                "result_message": f"Error: {str(e)}",
            })
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_close(self):
        """Close wizard and open trip purposes list."""
        return {
            "type": "ir.actions.act_window",
            "name": "Trip Purposes",
            "res_model": "gps.trip.purpose",
            "view_mode": "list,form",
            "target": "current",
        }
