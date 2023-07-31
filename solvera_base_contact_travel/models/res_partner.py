
import datetime
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta,date

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    nik = fields.Char(string='No NIK')
    id_customer = fields.Char(string='ID Customer')
    no_passport = fields.Char(string='Nomor Passport')
    passport_valid_date = fields.Date(string='Valid Passport')
    brith_date = fields.Date(string='Brith Of Date')
    
