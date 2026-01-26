from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestFleetVehicle(TransactionCase):
    """Test fleet.vehicle GPS extensions."""

    def setUp(self):
        super().setUp()
        self.vehicle_model = self.env["fleet.vehicle.model"].create(
            {
                "name": "Test Model",
                "brand_id": self.env["fleet.vehicle.model.brand"]
                .create({"name": "Test Brand"})
                .id,
            }
        )
        self.vehicle = self.env["fleet.vehicle"].create(
            {
                "model_id": self.vehicle_model.id,
                "license_plate": "TEST123",
                "imei": "123456789012345",
                "fuel_card_number": "CARD123",
            }
        )

    @patch("odoo.addons.gps_route_sheet.models.gps_db.GpsDbService.fetch_last_position")
    def test_compute_current_position(self, mock_fetch):
        """Test GPS position computation."""
        mock_fetch.return_value = {
            "latitude": 50.4501,
            "longitude": 30.5234,
            "speed": 60.0,
            "timestamp": "2024-01-26 12:00:00",
            "satellites": 12,
            "angle": 180.0,
            "odometer": 100000.0,
            "ignition": True,
            "fuel": 75.0,
            "battery": 13.5,
            "device_battery": 4.1,
        }

        self.vehicle._compute_current_position()

        self.assertEqual(self.vehicle.current_latitude, 50.4501)
        self.assertEqual(self.vehicle.current_longitude, 30.5234)
        self.assertEqual(self.vehicle.current_speed, 60.0)
        self.assertEqual(self.vehicle.current_satellites, 12)
        self.assertEqual(self.vehicle.current_odometer, 100000)
        self.assertTrue(self.vehicle.current_ignition)
        self.assertEqual(self.vehicle.gps_status, "Active")

    def test_compute_current_position_no_imei(self):
        """Test GPS position computation without IMEI."""
        vehicle = self.env["fleet.vehicle"].create(
            {
                "model_id": self.vehicle_model.id,
                "license_plate": "NOIMEI",
            }
        )

        vehicle._compute_current_position()

        self.assertEqual(vehicle.current_latitude, 0.0)
        self.assertEqual(vehicle.current_longitude, 0.0)
        self.assertEqual(vehicle.gps_status, "No IMEI")

    @patch("odoo.addons.gps_route_sheet.models.gps_db.GpsDbService.fetch_last_fuel_transaction")
    def test_compute_last_fuel_transaction(self, mock_fetch):
        """Test last fuel transaction computation."""
        mock_fetch.return_value = {
            "trans_date": "2024-01-26 10:00:00",
            "volume": 45.5,
            "amount": 2000.0,
            "station": "Test Station",
            "product": "A-95",
        }

        self.vehicle._compute_last_fuel_transaction()

        self.assertIsNotNone(self.vehicle.last_fuel_date)
        self.assertEqual(self.vehicle.last_fuel_volume, 45.5)
        self.assertEqual(self.vehicle.last_fuel_amount, 2000.0)

    def test_compute_last_fuel_transaction_no_card(self):
        """Test fuel transaction computation without fuel card."""
        vehicle = self.env["fleet.vehicle"].create(
            {
                "model_id": self.vehicle_model.id,
                "license_plate": "NOCARD",
            }
        )

        vehicle._compute_last_fuel_transaction()

        self.assertFalse(vehicle.last_fuel_date)
        self.assertEqual(vehicle.last_fuel_volume, 0.0)
        self.assertEqual(vehicle.last_fuel_amount, 0.0)

    @patch("odoo.addons.gps_route_sheet.models.gps_db.GpsDbService.fetch_last_position")
    def test_action_sync_odometer(self, mock_fetch):
        """Test odometer synchronization."""
        mock_fetch.return_value = {
            "odometer": 150000.0,
        }

        self.vehicle.action_sync_odometer()

        self.assertEqual(self.vehicle.odometer, 150000)

    @patch("odoo.addons.gps_route_sheet.models.gps_db.GpsDbService.fetch_last_position")
    def test_action_open_google_maps(self, mock_fetch):
        """Test Google Maps action."""
        mock_fetch.return_value = {
            "latitude": 50.4501,
            "longitude": 30.5234,
            "speed": 60.0,
            "timestamp": "2024-01-26 12:00:00",
            "satellites": 12,
            "angle": 180.0,
            "odometer": 100000.0,
            "ignition": True,
            "fuel": 75.0,
            "battery": 13.5,
            "device_battery": 4.1,
        }
        
        # Force recompute
        self.vehicle._compute_current_position()
        
        result = self.vehicle.action_open_google_maps()

        self.assertEqual(result["type"], "ir.actions.act_url")
        self.assertIn("google.com/maps", result["url"])
        self.assertIn("50.4501", result["url"])
        self.assertIn("30.5234", result["url"])

    def test_action_open_google_maps_no_coordinates(self):
        """Test Google Maps action without coordinates."""
        vehicle = self.env["fleet.vehicle"].create(
            {
                "model_id": self.vehicle_model.id,
                "license_plate": "NOCOORD",
            }
        )

        result = vehicle.action_open_google_maps()

        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(result["tag"], "display_notification")
        self.assertEqual(result["params"]["type"], "warning")
