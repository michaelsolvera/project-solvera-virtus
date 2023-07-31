
import datetime
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero

class Assetasset(models.Model):
    _inherit = 'account.asset.asset'


    def close_asset_solvera(self):
        asset_obj = self.env['account.asset.asset'].search([])
        for i in asset_obj:
            if i.value_residual == 0:
                i.write({'state': 'close'})
    def close_manual(self):
        for i in self:
            i.write({'state': 'close'})
    def open_manual(self):
        for i in self:
            i.write({'state': 'open'})
    
   