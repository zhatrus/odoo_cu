================
GPS Route Sheet
================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

|badge1| |badge2|

GPS tracking, route sheets, and fuel management for fleet vehicles.

**Table of contents**

.. contents::
   :local:

Overview
========

Comprehensive GPS tracking and fleet management solution for organizations
with vehicle fleets equipped with GPS trackers.

Key Features
============

* **Real-time GPS Tracking**: Monitor vehicle locations with IMEI-based integration
* **Automatic Trip Synchronization**: Configurable auto-sync from PostgreSQL database
* **Route Sheet Management**: Generate and print official route sheets
* **Fuel Transaction Tracking**: Monitor fuel consumption and analyze vs norms
* **Speed Violation Monitoring**: Automatic detection and alerts
* **Advanced Analytics**: Pivot tables and graphs for comprehensive analysis
* **Multi-level Access Control**: User and Manager roles with record rules

Technical Features
==================

* PostgreSQL external database connector for GPS data
* Automated synchronization (trips every 5 min, fuel hourly - configurable)
* Trip purpose classification system
* Integration with standard Odoo Fleet module
* Comprehensive demo data and Ukrainian translation included
* QWeb printable reports

Configuration
=============

1. Go to Settings > GPS Route Sheet Settings
2. Configure external PostgreSQL database connection:
   - Host
   - Port
   - Database name
   - Username
   - Password

3. Sync vehicles from GPS database using "Sync Vehicles from GPS" menu
4. Sync trip purposes using "Sync Trip Purposes from GPS" menu

Usage
=====

Creating Route Sheets
---------------------

1. Navigate to GPS Route Sheets > Route Sheets
2. Click "New"
3. Select vehicle and date range
4. Click "Import Trips" to load trips from GPS database
5. Review and adjust trip purposes
6. Print route sheet

GPS Tracking
------------

1. Navigate to GPS Route Sheets > GPS Tracking
2. View all vehicles with their current GPS positions
3. Click on a vehicle to see detailed information

Bug Tracker
===========

Bugs are tracked on GitHub Issues.

Credits
=======

Authors
-------

* Your Organization Name

Contributors
------------

* Your Name <your.email@example.com>

Maintainers
-----------

This module is maintained by Your Organization.

