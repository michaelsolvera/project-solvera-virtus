
import datetime
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta

class StockPicking(models.Model):
    _inherit = 'account.move'

    location_state = fields.Selection([
    ('jakarta', 'Jakarta'),
    ('solo', 'Solo'),
    ], string='Location', readonly=False, copy=False,store = True)