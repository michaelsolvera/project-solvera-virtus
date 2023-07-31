# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import fields, models


class AccountMoveDeposit(models.Model):
    _inherit = 'account.move'

    is_deposit = fields.Boolean(string='Is a Deposit', default=False)
