# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    amount_deposit = fields.Float(
        string='Deposit Amount', compute='_set_deposit_amount', store=True)

    @api.onchange('picking_id')
    def _onchange_picking_id(self):
        '''shows only deposit lines on return button'''
        res = super(ReturnPicking, self)._onchange_picking_id()
        moves = []
        if self.product_return_moves and self.env.context.get('deposit_refund'):
            for move in self.product_return_moves.filtered(
                lambda move: move.product_id.is_deposit or \
                move.product_id.is_container):
                moves.append(move.id)
            self.product_return_moves = [(6, 0, moves)]
        return res

    @api.depends('product_return_moves.quantity')
    def _set_deposit_amount(self):
        ''' it will compute deposit amount on return wizard. '''
        for order in self:
            amount_deposit = 0.0
            lines = []
            if order.picking_id and order.picking_id.purchase_id:
                lines = order.picking_id.purchase_id.order_line
            elif order.picking_id and order.picking_id.sale_id:
                lines = order.picking_id.sale_id.order_line
            for line in lines:
                for pick_ln in order.product_return_moves:
                    if line.product_id == pick_ln.product_id:
                        amount_deposit += line.price_unit * \
                            pick_ln.quantity
            order.update({
                'amount_deposit': amount_deposit,
            })


class ReturnPickingLine(models.TransientModel):
    _inherit = 'stock.return.picking.line'

    @api.constrains('quantity')
    def check_return_qty(self):
        ''' Add validation for return Qty '''
        for rec in self:
            data = self.wizard_id._prepare_stock_return_picking_line_vals_from_move(rec.move_id)
            qty = data.get('quantity', 0.00)
            if self.env.context.get('deposit_refund') and \
            rec.quantity and rec.move_id and \
            qty < rec.quantity:
                raise ValidationError(
                    _('Return quantity must be less than or equal to  Delivered Qty!'))
