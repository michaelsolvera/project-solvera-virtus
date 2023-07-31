# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import fields, models


class StockPickingDeposit(models.Model):
    _inherit = 'stock.picking'

    is_deposit_picking = fields.Boolean(
        string='Deposit Order', compute='_set_deposit_picking')

    def _set_deposit_picking(self):
        '''it will hide/show "return with deposit" button based on deposit lines.'''
        for rec in self:
            if rec.sale_id and rec.sale_id.order_line.mapped('is_deposit_order'):
                rec.is_deposit_picking = True
            elif rec.purchase_id and rec.purchase_id.order_line.mapped(
                'is_deposit_order'):
                rec.is_deposit_picking = True
            else:
                rec.is_deposit_picking = False

    def button_validate(self):
        '''it will hide/show "return deposit" button on sale or purchase order.'''
        res = super(StockPickingDeposit, self).button_validate()
        if res and self.env.context.get('deposit_refund'):
            for picking in self:
                if picking.sale_id:
                    picking.sale_id.is_refund_deposit = True
                elif picking.purchase_id:
                    picking.purchase_id.is_refund_deposit = True
        return res
