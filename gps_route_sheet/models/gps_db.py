import psycopg2

from odoo import models
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
            raise UserError("GPS database connection is not configured.")
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
