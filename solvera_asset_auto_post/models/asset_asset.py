
import datetime
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero

class Assetasset(models.Model):
    _inherit = 'account.move'

    def backup_auto_post(self):
        je_obj = self.env['account.move'].search([('asset_depreciation_ids',"!=",False),('move_type','=','entry'),('state','=','draft')])

        for i in je_obj:
            if i.auto_post == False:
                i.auto_post = True