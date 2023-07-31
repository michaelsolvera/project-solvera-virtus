from urllib3 import Retry
from odoo import fields,models,api
from datetime import datetime,date,timedelta
from odoo.exceptions import UserError
import random,string


class AutoPost(models.Model):
    _inherit = 'res.partner'
    
    token = fields.Char(string='Token')

    def get_token(self,*partners): 
        S = 36
        partner = partners
        partner_obj = self.env['res.partner'].search([('id','=',partner[0])])
        for this in partner_obj:  
            gettoken = ''.join(random.choices(string.ascii_uppercase +string.ascii_lowercase+ string.digits, k = S))    
            this.write({'token': gettoken})

        return True