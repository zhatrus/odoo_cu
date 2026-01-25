from odoo import api, fields, models
from odoo.exceptions import UserError


class VehicleSyncWizard(models.TransientModel):
    """Wizard for synchronizing vehicles from PostgreSQL GPS database."""

    _name = "vehicle.sync.wizard"
    _description = "Vehicle Synchronization Wizard"

    sync_mode = fields.Selection(
        [
            ("create_new", "Create New Vehicles Only"),
            ("update_existing", "Update Existing Vehicles"),
            ("create_and_update", "Create New and Update Existing"),
        ],
        string="Sync Mode",
        default="create_and_update",
        required=True,
        help="Choose how to synchronize vehicles from GPS database",
    )
    vehicle_count = fields.Integer(
        string="Vehicles Found",
        readonly=True,
    )
    result_message = fields.Text(
        string="Result",
        readonly=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("done", "Done"),
        ],
        default="draft",
    )

    def action_sync_vehicles(self):
        """Synchronize vehicles from PostgreSQL database."""
        self.ensure_one()

        try:
            gps_service = self.env["gps.db.service"]
            vehicles_data = gps_service.fetch_vehicles()

            if not vehicles_data:
                raise UserError("No vehicles found in GPS database.")

            created_count = 0
            updated_count = 0
            skipped_count = 0

            for vehicle_data in vehicles_data:
                (
                    pg_id,
                    imei,
                    s_n,
                    reg_number,
                    vehicle_model,
                    fuel_card_number,
                    fuel_norm,
                    sim_number,
                    alias,
                ) = vehicle_data

                if not imei:
                    skipped_count += 1
                    continue

                existing_vehicle = self.env["fleet.vehicle"].search(
                    [("imei", "=", imei)], limit=1
                )

                vehicle_vals = {
                    "imei": imei,
                    "gps_tracker_sn": s_n,
                    "license_plate": reg_number,
                    "model_id": self._get_or_create_vehicle_model(vehicle_model),
                    "fuel_card_number": fuel_card_number,
                    "fuel_norm_l_100km": float(fuel_norm) if fuel_norm else 0.0,
                    "sim_number": sim_number,
                    "gps_alias": alias,
                }

                if existing_vehicle:
                    if self.sync_mode in ("update_existing", "create_and_update"):
                        existing_vehicle.write(vehicle_vals)
                        updated_count += 1
                    else:
                        skipped_count += 1
                else:
                    if self.sync_mode in ("create_new", "create_and_update"):
                        self.env["fleet.vehicle"].create(vehicle_vals)
                        created_count += 1
                    else:
                        skipped_count += 1

            result_msg = (
                f"Synchronization completed:\n"
                f"- Created: {created_count}\n"
                f"- Updated: {updated_count}\n"
                f"- Skipped: {skipped_count}\n"
                f"- Total processed: {len(vehicles_data)}"
            )

            self.write(
                {
                    "vehicle_count": len(vehicles_data),
                    "result_message": result_msg,
                    "state": "done",
                }
            )

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Synchronization Successful",
                    "message": result_msg,
                    "type": "success",
                    "sticky": False,
                },
            }

        except UserError as e:
            raise e
        except (ConnectionError, KeyError, ValueError) as e:
            raise UserError(f"Synchronization failed: {str(e)}") from e

    def _get_or_create_vehicle_model(self, model_name):
        """Get or create fleet.vehicle.model by name."""
        if not model_name:
            return False

        vehicle_model = self.env["fleet.vehicle.model"].search(
            [("name", "=", model_name)], limit=1
        )
        if not vehicle_model:
            # Extract brand from model_name (e.g., "Ford/Focus" -> "Ford")
            brand_name = model_name.split("/")[0] if "/" in model_name else "Unknown"
            
            # Get or create brand
            brand = self.env["fleet.vehicle.model.brand"].search(
                [("name", "=", brand_name)], limit=1
            )
            if not brand:
                brand = self.env["fleet.vehicle.model.brand"].create(
                    {"name": brand_name}
                )
            
            vehicle_model = self.env["fleet.vehicle.model"].create(
                {
                    "name": model_name,
                    "brand_id": brand.id,
                }
            )
        return vehicle_model.id

    def action_close(self):
        """Close wizard and return to vehicles list."""
        return {
            "type": "ir.actions.act_window",
            "name": "Vehicles",
            "res_model": "fleet.vehicle",
            "view_mode": "tree,form",
            "domain": [("imei", "!=", False)],
        }
