from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestVehicleSyncWizard(TransactionCase):
    """Test vehicle synchronization wizard."""

    def setUp(self):
        super().setUp()
        self.wizard = self.env["vehicle.sync.wizard"].create(
            {"sync_mode": "create_and_update"}
        )

    @patch("odoo.addons.gps_route_sheet.models.gps_db.GpsDbService.fetch_vehicles")
    def test_action_sync_vehicles_create_new(self, mock_fetch):
        """Test creating new vehicles from GPS database."""
        mock_fetch.return_value = [
            (
                1,
                "123456789012345",
                "SN001",
                "TEST123",
                "Ford/Focus",
                "CARD123",
                8.5,
                "SIM001",
                "Alias1",
            ),
        ]

        wizard = self.env["vehicle.sync.wizard"].create(
            {"sync_mode": "create_new"}
        )
        result = wizard.action_sync_vehicles()

        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(result["tag"], "display_notification")
        self.assertEqual(result["params"]["type"], "success")

        # Verify vehicle was created
        vehicle = self.env["fleet.vehicle"].search(
            [("imei", "=", "123456789012345")]
        )
        self.assertEqual(len(vehicle), 1)
        self.assertEqual(vehicle.license_plate, "TEST123")
        self.assertEqual(vehicle.fuel_card_number, "CARD123")

    @patch("odoo.addons.gps_route_sheet.models.gps_db.GpsDbService.fetch_vehicles")
    def test_action_sync_vehicles_update_existing(self, mock_fetch):
        """Test updating existing vehicles from GPS database."""
        # Create existing vehicle
        brand = self.env["fleet.vehicle.model.brand"].create(
            {"name": "Ford"}
        )
        model = self.env["fleet.vehicle.model"].create(
            {"name": "Ford/Focus", "brand_id": brand.id}
        )
        vehicle = self.env["fleet.vehicle"].create(
            {
                "model_id": model.id,
                "license_plate": "OLD123",
                "imei": "123456789012345",
            }
        )

        mock_fetch.return_value = [
            (
                1,
                "123456789012345",
                "SN001",
                "NEW123",
                "Ford/Focus",
                "CARD123",
                8.5,
                "SIM001",
                "Alias1",
            ),
        ]

        wizard = self.env["vehicle.sync.wizard"].create(
            {"sync_mode": "update_existing"}
        )
        result = wizard.action_sync_vehicles()

        self.assertEqual(result["type"], "ir.actions.client")
        
        # Verify vehicle was updated
        vehicle.invalidate_recordset()
        self.assertEqual(vehicle.license_plate, "NEW123")
        self.assertEqual(vehicle.fuel_card_number, "CARD123")

    @patch("odoo.addons.gps_route_sheet.models.gps_db.GpsDbService.fetch_vehicles")
    def test_action_sync_vehicles_skip_no_imei(self, mock_fetch):
        """Test skipping vehicles without IMEI."""
        mock_fetch.return_value = [
            (
                1,
                None,  # No IMEI
                "SN001",
                "TEST123",
                "Ford/Focus",
                "CARD123",
                8.5,
                "SIM001",
                "Alias1",
            ),
        ]

        result = self.wizard.action_sync_vehicles()

        self.assertEqual(result["type"], "ir.actions.client")
        
        # Verify no vehicle was created
        vehicle = self.env["fleet.vehicle"].search(
            [("license_plate", "=", "TEST123")]
        )
        self.assertEqual(len(vehicle), 0)

    @patch("odoo.addons.gps_route_sheet.models.gps_db.GpsDbService.fetch_vehicles")
    def test_action_sync_vehicles_no_data(self, mock_fetch):
        """Test synchronization with no vehicles in GPS database."""
        mock_fetch.return_value = []

        with self.assertRaises(UserError) as context:
            self.wizard.action_sync_vehicles()
        
        self.assertIn("No vehicles found", str(context.exception))

    @patch("odoo.addons.gps_route_sheet.models.gps_db.GpsDbService.fetch_vehicles")
    def test_get_or_create_vehicle_model(self, mock_fetch):
        """Test vehicle model creation."""
        mock_fetch.return_value = [
            (
                1,
                "123456789012345",
                "SN001",
                "TEST123",
                "Toyota/Camry",
                "CARD123",
                8.5,
                "SIM001",
                "Alias1",
            ),
        ]

        self.wizard.action_sync_vehicles()

        # Verify brand and model were created
        brand = self.env["fleet.vehicle.model.brand"].search(
            [("name", "=", "Toyota")]
        )
        self.assertEqual(len(brand), 1)

        model = self.env["fleet.vehicle.model"].search(
            [("name", "=", "Toyota/Camry")]
        )
        self.assertEqual(len(model), 1)
        self.assertEqual(model.brand_id, brand)

    def test_action_close(self):
        """Test wizard close action."""
        result = self.wizard.action_close()

        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "fleet.vehicle")
        self.assertEqual(result["view_mode"], "tree,form")
