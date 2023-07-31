# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaleOrderDeposit(models.Model):
    _inherit = 'sale.order'

    deposit_order_count = fields.Integer(
        string='Deposit Order', compute='_set_do_count')
    amount_deposit = fields.Monetary(
        string='Deposit Amount', compute='_set_deposit_amount', store=True)
    is_refund_deposit = fields.Boolean(string='Refund order', default=False)

    @api.depends('order_line.price_total')
    def _set_deposit_amount(self):
        '''it will compute amount deposit based on orderlines.'''
        for order in self:
            amount_deposit = 0.0
            for line in order.order_line:
                if line.product_id and line.product_id.is_deposit or \
                line.product_id.is_container:
                    amount_deposit += line.price_subtotal
            order.update({
                'amount_deposit': amount_deposit,
                'amount_untaxed': order.amount_untaxed - amount_deposit,
                'amount_total': order.amount_total + amount_deposit,
            })

    def action_set_deposit_product(self):
        '''Add associated deposit/container line based on order lines.'''
        sale_order_line = self.env['sale.order.line']
        for rec in self.order_line:
            ##raise validation for adding product
            if rec.product_id and rec.product_id.container_product_id and \
            rec.product_uom_qty % rec.product_id.container_product_id.container_qty != 0:
                raise ValidationError(
                    _("Please set product %s quantity in Multiply of %s") % \
                    (rec.product_id.display_name, rec.product_id.container_product_id.container_qty))
            ##deposit line code
            if rec.product_id and rec.product_id.deposit_product_id and not \
            rec.deposit_line_id:
                rec.deposit_line_id = sale_order_line.create({
                    'product_id': rec.product_id.deposit_product_id.id,
                    'product_uom_qty': rec.product_uom_qty,
                    'qty_delivered_method': rec.qty_delivered_method,
                    'qty_delivered':rec.qty_delivered,
                    'price_unit': rec.product_id.sale_deposit_price,
                    'sequence': rec.sequence+1,
                    'parent_id': rec.id,
                    'order_id': self.id
                }).id
            elif rec.product_id and rec.product_id.deposit_product_id and \
            rec.deposit_line_id:
                rec.deposit_line_id.write({
                    'product_id': rec.product_id.deposit_product_id.id,
                    'name': rec.product_id.deposit_product_id.name,
                    'parent_id': rec.id,
                    'product_uom_qty': rec.product_uom_qty,
                    'price_unit': rec.product_id.sale_deposit_price,
                    'qty_delivered_method': rec.qty_delivered_method,
                    'qty_delivered': rec.qty_delivered,
                })
            ##container line code
            if rec.product_id and rec.product_id.container_product_id and not \
            rec.container_line_id:
                rec.container_line_id = sale_order_line.create({
                    'product_id': rec.product_id.container_product_id.id,
                    'product_uom_qty': rec.product_uom_qty / \
                    rec.product_id.container_product_id.container_qty,
                    'qty_delivered_method': rec.qty_delivered_method,
                    'qty_delivered':rec.qty_delivered,
                    'price_unit': rec.product_id.sale_container_price,
                    'sequence': rec.sequence+1,
                    'parent_id': rec.id,
                    'order_id': self.id
                }).id
            elif rec.product_id and rec.product_id.container_product_id and \
            rec.container_line_id:
                rec.container_line_id.write({
                    'product_id': rec.product_id.container_product_id.id,
                    'name': rec.product_id.container_product_id.name,
                    'parent_id': rec.id,
                    'product_uom_qty': rec.product_uom_qty / \
                    rec.product_id.container_product_id.container_qty,
                    'price_unit': rec.product_id.sale_container_price,
                    'qty_delivered_method': rec.qty_delivered_method,
                    'qty_delivered': rec.qty_delivered,
                })

    def action_confirm(self):
        '''On confirm button Add/Check deposit/container product.'''
        res = super(SaleOrderDeposit, self).action_confirm()
        for record in self:
            record.action_set_deposit_product()
        return res

    def _set_do_count(self):
        '''return deposit/container order count on smart button.'''
        for record in self:
            if record.state not in ['draft','cancel'] and \
                record.order_line.filtered('is_deposit_order'):
                record.deposit_order_count = len(record.order_line.filtered(
                    'is_deposit_order'))
            else:
                record.deposit_order_count = 0

    def _get_invoiceable_lines(self, final=False):
        '''it will bypass all product to only generate invoice with 
            deposit/container product on button click.'''
        invoiceable_lines = super()._get_invoiceable_lines(final)
        invoiceable_deposit_lines = []
        if self.env.context.get('deposit_order_refund'):
            for invoice_line in invoiceable_lines:
                if invoice_line.is_deposit_order and \
                    invoice_line.qty_to_invoice < 0:
                    invoice_line.price_subdeposit += abs(
                        invoice_line.qty_to_invoice) * invoice_line.price_unit
                    invoiceable_deposit_lines.append(invoice_line.id)
            line_ids = self.env['sale.order.line'].browse(
                invoiceable_deposit_lines)
            if not line_ids:
                raise ValidationError(_('Refund already collected !!'))
            return line_ids

        else:
            return invoiceable_lines

    def generate_credit_note(self):
        '''it will generate customer refund invoice based on deposit/container product.'''
        invoice = self._create_invoices(final=True)
        if invoice:
            invoice.is_deposit = True
        return self.action_view_invoice()

    def get_orders(self, date_range, customer):
        '''Return orders based on report filters.'''
        start_date = datetime.strptime(
            date_range[1]+' '+'23:59:59', DEFAULT_SERVER_DATETIME_FORMAT)
        end_date = datetime.strptime(
            date_range[0]+' '+'00:00:00', DEFAULT_SERVER_DATETIME_FORMAT)
        if customer:
            partner = self.env['res.partner'].browse(customer)
            return self.search([('date_order','<=',start_date),
                ('date_order','>=',end_date),('partner_id','=',partner.id),
                ('company_id','in',self.env.context.get('allowed_company_ids'))])
        else:
            return self.search([('date_order','<=',start_date),
                ('date_order','>=',end_date),
                ('company_id','in',self.env.context.get('allowed_company_ids'))])

    def _get_customer_deposit_reports_values(self, date_range, customer):
        '''return sale orders on reports (customer filters).'''
        return self.get_orders(date_range, customer)

    def _get_deposit_reports_values(self, date_range):
        '''return All sale orders on reports.'''
        return self.get_orders(date_range, customer=False)

    def _get_return_value(self):
        '''return total returned amount on report.'''
        return_val = 0
        for line in self.order_line:
            if line.is_deposit_order and line.return_qty:
                return_val += line.return_qty * line.price_unit
        return return_val


class SaleOrderLineDeposit(models.Model):
    _inherit = 'sale.order.line'

    return_qty = fields.Float(string='Return Qty', readonly=True)
    deliver_qty = fields.Float(string='Actual Deliver Qty', readonly=True)
    price_subdeposit = fields.Float(
        string='Return Value', readonly=True, default=0.00)
    is_deposit_order = fields.Boolean(
        string='Deposit Order', compute='_set_deposit_order', store=True)
    deposit_line_id = fields.Many2one('sale.order.line', string='Deposit Line',
        ondelete='cascade')
    parent_id = fields.Many2one('sale.order.line', ondelete='cascade',
        readonly=True)
    price_deposit_total = fields.Float(
        string='Deposit Amount', readonly=True, 
        compute='_set_total_deposit_amount')
    ##container field
    container_line_id = fields.Many2one('sale.order.line', string='Container Line',
        ondelete='cascade')

    @api.depends('product_id')
    def _set_deposit_order(self):
        '''compute order line is deposit or not.'''
        for line in self:
            if line.product_id and \
            line.product_id.is_deposit or line.product_id.is_container:
                line.is_deposit_order = True
            else:
                line.is_deposit_order = False

    def _set_total_deposit_amount(self):
        '''Shows only Inv done amount on deposit/container page'''
        for record in self:
            if any(invoice.move_id.move_type == 'out_invoice' and \
                invoice.move_id.state == 'posted' \
                for invoice in record.invoice_lines):
                record.price_deposit_total = record.price_subtotal
            else:
                record.price_deposit_total = float(0.00)

    @api.depends('qty_delivered_method')
    def _compute_qty_delivered(self):
        '''it will compute return qty on sale lines.'''
        res = super(SaleOrderLineDeposit, self)._compute_qty_delivered()
        for line in self:
            qty = delivery_qty = 0.00
            outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
            for move in incoming_moves:
                if move.state != 'done':
                    qty += move.product_uom._compute_quantity(
                            move.product_uom_qty, line.product_uom,
                            rounding_method='HALF-UP')
            for out_move in outgoing_moves:
                if out_move.state != 'done':
                    continue
                delivery_qty += out_move.product_uom._compute_quantity(
                                out_move.product_uom_qty, line.product_uom,
                                rounding_method='HALF-UP')
            line.write({'return_qty':line.return_qty + qty,
                        'deliver_qty':delivery_qty,})
        return res
