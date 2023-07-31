
import datetime
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta,date

class CollectionOrder(models.Model):
    _inherit = "res.users"

    related_partner = fields.Many2many("res.users","related_user_ids_rel","related_partner_id","related_user_id" ,string="Related User",copy=False)
