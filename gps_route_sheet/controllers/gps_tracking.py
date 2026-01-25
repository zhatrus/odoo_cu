import json

from odoo import http
from odoo.http import request


class GpsTrackingController(http.Controller):
    """Controller for GPS tracking and fleet monitoring."""

    @http.route("/gps/tracking/map", type="http", auth="user", website=True)
    def tracking_map(self, **kwargs):
        """Render GPS tracking map page."""
        return request.render("gps_route_sheet.gps_tracking_map")

    @http.route("/gps/tracking/vehicles", type="json", auth="user")
    def get_vehicles_positions(self, **kwargs):
        """Get all vehicles with their current GPS positions."""
        vehicles = request.env["fleet.vehicle"].search([("imei", "!=", False)])
        result = []
        for vehicle in vehicles:
            if vehicle.current_latitude and vehicle.current_longitude:
                result.append(
                    {
                        "id": vehicle.id,
                        "name": vehicle.display_name,
                        "license_plate": vehicle.license_plate,
                        "imei": vehicle.imei,
                        "latitude": vehicle.current_latitude,
                        "longitude": vehicle.current_longitude,
                        "last_update": (
                            vehicle.last_position_time.isoformat()
                            if vehicle.last_position_time
                            else None
                        ),
                        "status": vehicle.gps_status,
                    }
                )
        return result

    @http.route("/gps/tracking/vehicle/<int:vehicle_id>", type="json", auth="user")
    def get_vehicle_details(self, vehicle_id, **kwargs):
        """Get detailed GPS information for a specific vehicle."""
        vehicle = request.env["fleet.vehicle"].browse(vehicle_id)
        if not vehicle.exists() or not vehicle.imei:
            return {"error": "Vehicle not found or no IMEI"}

        try:
            gps_service = request.env["gps.db.service"]
            position = gps_service.fetch_last_position(vehicle.imei)
            if position:
                return {
                    "id": vehicle.id,
                    "name": vehicle.display_name,
                    "license_plate": vehicle.license_plate,
                    "imei": vehicle.imei,
                    "latitude": position.get("latitude"),
                    "longitude": position.get("longitude"),
                    "speed": position.get("speed"),
                    "timestamp": (
                        position.get("timestamp").isoformat()
                        if position.get("timestamp")
                        else None
                    ),
                    "satellites": position.get("satellites"),
                    "angle": position.get("angle"),
                    "odometer": position.get("odometer"),
                    "ignition": position.get("ignition"),
                    "fuel": position.get("fuel"),
                    "battery": position.get("battery"),
                }
            return {"error": "No GPS data available"}
        except Exception as e:
            return {"error": str(e)}
