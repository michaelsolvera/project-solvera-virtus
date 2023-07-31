

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    travel_agent_boolean = fields.Boolean(string="Travel Agent")