
import datetime
from odoo import models, fields, api,_
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero

class Assetasset(models.Model):
    _inherit = 'account.move'

    def action_register_payment(self):
        login = self.env.user.has_group('solvera_accounting_sales.access_for_user_group')
        if login == False:
            raise UserError(('You Can not Register Payment'))
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    
    
   