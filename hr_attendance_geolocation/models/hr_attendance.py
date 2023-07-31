# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import requests
import json
import urllib
from geopy.geocoders import Nominatim
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare



class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    check_in_latitude = fields.Float(
        "Check-in Latitude", digits="Location", readonly=True
    )
    check_in_longitude = fields.Float(
        "Check-in Longitude", digits="Location", readonly=True
    )
    check_out_latitude = fields.Float(
        "Check-out Latitude", digits="Location", readonly=True
    )
    check_out_longitude = fields.Float(
        "Check-out Longitude", digits="Location", readonly=True
    )
    url_checkin = fields.Char('URL Check In',compute="get_url_maps_in")
    address_url = fields.Char('URL Check In',compute="get_url_maps_in")
    url_checkout = fields.Char('URL Check Out',compute="get_url_maps_out")
    address_url_out = fields.Char('URL Check In',compute="get_url_maps_out")
    @api.depends("check_in_latitude","check_in_longitude","check_out_latitude","check_out_longitude")
    def get_url_maps_in(self):
        geolocator = Nominatim(user_agent="hr_attendance_geolocation")
        
        for i in self:
            if i.check_in_latitude and i.check_in_longitude:
                coordinate = str(i.check_in_latitude)+','+str(i.check_in_longitude)
                location_maps = geolocator.reverse(coordinate)
                i.url_checkin = 'https://maps.google.com/?q='+str(i.check_in_latitude)+','+str(i.check_in_longitude)
                i.address_url = location_maps.address

            else:
                 i.url_checkin = None
                 i.address_url = None

    @api.depends("check_in_latitude","check_in_longitude","check_out_latitude","check_out_longitude") 
    def get_url_maps_out(self):
        for i in self:
            geolocator = Nominatim(user_agent="hr_attendance_geolocation")
            if i.check_out_latitude and i.check_out_longitude:
                coordinate = str(i.check_out_latitude)+','+str(i.check_out_longitude)
                location_maps = geolocator.reverse(coordinate)
                i.url_checkout = 'https://maps.google.com/?q='+str(i.check_out_latitude)+','+str(i.check_out_longitude)
                i.address_url_out = location_maps.address
            else:
                i.url_checkout = None
                i.address_url_out = None


    
