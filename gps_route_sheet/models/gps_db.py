import psycopg2

from odoo import _, models
from odoo.exceptions import UserError


class GpsDbService(models.AbstractModel):
    _name = "gps.db.service"
    _description = "GPS DB Service"

    def _get_db_params(self):
        config = self.env["ir.config_parameter"].sudo()
        host = config.get_param("gps_route_sheet.db_host")
        port = config.get_param("gps_route_sheet.db_port")
        dbname = config.get_param("gps_route_sheet.db_name")
        user = config.get_param("gps_route_sheet.db_user")
        password = config.get_param("gps_route_sheet.db_password")
        if not all([host, port, dbname, user, password]):
            raise UserError(
                _("GPS database connection is not configured.")
            )
        return {
            "host": host,
            "port": int(port),
            "dbname": dbname,
            "user": user,
            "password": password,
        }

    def fetch_trips(self, imei, date_from, date_to):
        params = self._get_db_params()
        query = """
            SELECT
                id,
                trip_date,
                route_description,
                trip_purpose_id,
                trip_purpose_other,
                in_city_km,
                outside_city_km,
                total_km,
                city_coefficient,
                outside_coefficient,
                fuel_liters,
                project_name,
                payment_type,
                driver_name,
                user_comment
            FROM tracker_trips
            WHERE imei = %s
              AND trip_date BETWEEN %s AND %s
            ORDER BY trip_date, id
        """
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (imei, date_from, date_to))
                return cursor.fetchall()

    def fetch_trip_purposes(self):
        params = self._get_db_params()
        query = """
            SELECT
                id,
                code,
                name_uk,
                description,
                is_active,
                sort_order
            FROM trip_purposes
            ORDER BY sort_order, name_uk
        """
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()

    def fetch_last_position(self, imei):
        """Fetch last GPS position for vehicle by IMEI."""
        params = self._get_db_params()
        query = """
            SELECT
                latitude,
                longitude,
                speed,
                timestamp,
                satellites,
                angle,
                odometer,
                ignition,
                fuel,
                battery
            FROM tracker_positions
            WHERE imei = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (imei,))
                row = cursor.fetchone()
                if row:
                    return {
                        "latitude": row[0],
                        "longitude": row[1],
                        "speed": row[2],
                        "timestamp": row[3],
                        "satellites": row[4],
                        "angle": row[5],
                        "odometer": row[6],
                        "ignition": row[7],
                        "fuel": row[8],
                        "battery": row[9],
                    }
                return None

    def fetch_vehicles(self):
        """Fetch all vehicles from PostgreSQL database."""
        params = self._get_db_params()
        query = """
            SELECT
                id,
                imei,
                s_n,
                reg_number,
                vehicle_model,
                fuel_card_number,
                fuel_norm_l_100km,
                sim_number,
                alias
            FROM vehicles
            ORDER BY reg_number
        """
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()

    def fetch_all_positions(self):
        """Fetch last GPS positions for all vehicles."""
        params = self._get_db_params()
        query = """
            SELECT DISTINCT ON (imei)
                imei,
                latitude,
                longitude,
                speed,
                timestamp,
                satellites,
                angle,
                odometer,
                ignition,
                fuel,
                battery
            FROM tracker_positions
            ORDER BY imei, timestamp DESC
        """
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()

    def test_connection(self):
        """Test connection to GPS PostgreSQL database."""
        params = self._get_db_params()
        with psycopg2.connect(**params):
            return True
