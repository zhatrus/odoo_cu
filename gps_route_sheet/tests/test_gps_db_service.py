from unittest.mock import MagicMock, patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestGpsDbService(TransactionCase):
    """Test GPS database service."""

    def setUp(self):
        super().setUp()
        self.gps_service = self.env["gps.db.service"]
        
        # Set up test configuration
        config = self.env["ir.config_parameter"].sudo()
        config.set_param("gps_route_sheet.db_host", "localhost")
        config.set_param("gps_route_sheet.db_port", "5432")
        config.set_param("gps_route_sheet.db_name", "test_db")
        config.set_param("gps_route_sheet.db_user", "test_user")
        config.set_param("gps_route_sheet.db_password", "test_pass")

    def test_get_db_params(self):
        """Test database parameters retrieval."""
        params = self.gps_service._get_db_params()
        
        self.assertEqual(params["host"], "localhost")
        self.assertEqual(params["port"], 5432)
        self.assertEqual(params["dbname"], "test_db")
        self.assertEqual(params["user"], "test_user")
        self.assertEqual(params["password"], "test_pass")

    def test_get_db_params_missing_config(self):
        """Test database parameters with missing configuration."""
        config = self.env["ir.config_parameter"].sudo()
        config.set_param("gps_route_sheet.db_host", False)
        
        with self.assertRaises(UserError):
            self.gps_service._get_db_params()

    @patch("psycopg2.connect")
    def test_fetch_last_position(self, mock_connect):
        """Test fetching last GPS position."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (
            50.4501,  # latitude
            30.5234,  # longitude
            60.0,     # speed
            "2024-01-26 12:00:00",  # timestamp
            12,       # satellites
            180.0,    # angle
            100000.0, # odometer
            True,     # ignition
            75.0,     # fuel
            13.5,     # battery
            4.1,      # device_battery
        )
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = self.gps_service.fetch_last_position("123456789012345")

        self.assertIsNotNone(result)
        self.assertEqual(result["latitude"], 50.4501)
        self.assertEqual(result["longitude"], 30.5234)
        self.assertEqual(result["speed"], 60.0)
        self.assertEqual(result["satellites"], 12)
        self.assertEqual(result["odometer"], 100000.0)
        self.assertTrue(result["ignition"])

    @patch("psycopg2.connect")
    def test_fetch_last_position_no_data(self, mock_connect):
        """Test fetching GPS position with no data."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = self.gps_service.fetch_last_position("999999999999999")

        self.assertIsNone(result)

    @patch("psycopg2.connect")
    def test_fetch_last_fuel_transaction(self, mock_connect):
        """Test fetching last fuel transaction."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (
            "2024-01-26 10:00:00",  # trans_date
            45.5,                    # volume
            2000.0,                  # amount
            "Test Station",          # station
            "A-95",                  # product
        )
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = self.gps_service.fetch_last_fuel_transaction("CARD123")

        self.assertIsNotNone(result)
        self.assertEqual(result["trans_date"], "2024-01-26 10:00:00")
        self.assertEqual(result["volume"], 45.5)
        self.assertEqual(result["amount"], 2000.0)
        self.assertEqual(result["station"], "Test Station")
        self.assertEqual(result["product"], "A-95")

    def test_fetch_last_fuel_transaction_no_card(self):
        """Test fetching fuel transaction without card number."""
        result = self.gps_service.fetch_last_fuel_transaction(None)
        
        self.assertIsNone(result)

    @patch("psycopg2.connect")
    def test_fetch_vehicles(self, mock_connect):
        """Test fetching vehicles from GPS database."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, "123456789012345", "SN001", "TEST123", "Test Model", 
             "CARD123", 8.5, "SIM001", "Alias1"),
            (2, "543210987654321", "SN002", "TEST456", "Test Model 2", 
             "CARD456", 9.0, "SIM002", "Alias2"),
        ]
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = self.gps_service.fetch_vehicles()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][1], "123456789012345")  # IMEI
        self.assertEqual(result[0][3], "TEST123")  # reg_number
        self.assertEqual(result[1][1], "543210987654321")

    @patch("psycopg2.connect")
    def test_test_connection_success(self, mock_connect):
        """Test successful database connection."""
        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn

        result = self.gps_service.test_connection()

        self.assertTrue(result)

    @patch("psycopg2.connect")
    def test_test_connection_failure(self, mock_connect):
        """Test failed database connection."""
        mock_connect.side_effect = Exception("Connection failed")

        with self.assertRaises(Exception):
            self.gps_service.test_connection()
