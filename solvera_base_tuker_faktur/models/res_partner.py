
import datetime
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    @api.model
    def create(self, values):

        res = super(ResPartner, self).create(values)
        for i in res:
            if i.parent_id.tukar_faktur_allow == True:
                i.tukar_faktur_allow = True
        return res