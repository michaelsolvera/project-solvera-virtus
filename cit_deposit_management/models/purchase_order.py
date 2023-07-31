# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from itertools import groupby
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrderDeposit(models.Model):
    _inherit = 'purchase.order'

    deposit_order_count = fields.Integer(
        string='Deposit Order', compute='_set_purchase_ol_count')
    amount_deposit = fields.Monetary(
        string='Deposit Amount', compute='_set_deposit_purchase_amount',
        store=True)
    is_refund_deposit = fields.Boolean(string='Refund order', default=False)

    @api.depends('order_line.price_total')
    def _set_deposit_purchase_amount(self):
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
        '''Add associated deposit line based on order lines.'''
        purchase_line = self.env['purchase.order.line']
        for rec in self.order_line:
            ##raise validation for adding product
            if rec.product_id and rec.product_id.container_product_id and \
            rec.product_qty % rec.product_id.container_product_id.container_qty != 0:
                raise ValidationError(
                    _("Please set product %s quantity in Multiply of %s") % \
                    (rec.product_id.display_name, rec.product_id.container_product_id.container_qty))
            ##deposit line code
            if rec.product_id and rec.product_id.deposit_product_id and \
                not rec.deposit_line_id:
                rec.deposit_line_id = purchase_line.create({
                    'product_id': rec.product_id.deposit_product_id.id,
                    'product_qty': rec.product_qty,
                    'price_unit': rec.product_id.purchase_deposit_price,
                    'sequence':rec.sequence+1,
                    'parent_id':rec.id,
                    'order_id':self.id
                }).id
            elif rec.product_id and rec.product_id.deposit_product_id and \
                rec.deposit_line_id:
                rec.deposit_line_id.write({
                    'product_id': rec.product_id.deposit_product_id.id,
                    'parent_id':rec.id,
                    'name': rec.product_id.deposit_product_id.name,
                    'product_qty': rec.product_qty,
                    'price_unit': rec.product_id.purchase_deposit_price
                })
            ##container line code
            if rec.product_id and rec.product_id.container_product_id and not \
            rec.container_line_id:
                rec.container_line_id = purchase_line.create({
                    'product_id': rec.product_id.container_product_id.id,
                    'product_qty': rec.product_qty / \
                    rec.product_id.container_product_id.container_qty,
                    'price_unit': rec.product_id.purchase_container_price,
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
                    'product_qty': rec.product_qty / \
                    rec.product_id.container_product_id.container_qty,
                    'price_unit': rec.product_id.purchase_container_price,
                })

    def button_confirm(self):
        '''On confirm button Add/Check deposit/container product.'''
        res = super(PurchaseOrderDeposit, self).button_confirm()
        for record in self:
            record.action_set_deposit_product()
        return res

    def _set_purchase_ol_count(self):
        '''return deposit order count on smart button.'''
        for record in self:
            if record.state not in ['draft', 'cancel'] and \
                record.order_line.filtered('is_deposit_order'):
                record.deposit_order_count = len(record.order_line.filtered(
                    'is_deposit_order'))
            else:
                record.deposit_order_count = 0

    def generate_vendor_credit_note(self):
        '''Override base method for generate refund invoice for only deposit 
            products.'''
        invoice_vals_list = []
        for order in self:
            if order.invoice_status != 'to invoice':
                continue
            order = order.with_company(order.company_id)
            pending_section = None
            invoice_vals = order._prepare_invoice()
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if line.is_deposit_order and line.qty_to_invoice < 0:
                    line.price_subdeposit += abs(line.qty_to_invoice) * line.price_unit
                    if pending_section:
                        invoice_vals['invoice_line_ids'].append(
                            (0, 0, pending_section._prepare_account_move_line())
                            )
                        pending_section = None
                    invoice_vals['invoice_line_ids'].append(
                        (0, 0, line._prepare_account_move_line())
                        )
            invoice_vals_list.append(invoice_vals)
        if not invoice_vals_list[0]['invoice_line_ids']:
            raise UserError(_('Refund already collected !!'))

        new_invoice_vals_list = []
        for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (
            x.get('company_id'), x.get('partner_id'), x.get('currency_id'))):
            origins = set()
            payment_refs = set()
            refs = set()
            ref_invoice_vals = None
            for invoice_vals in invoices:
                if not ref_invoice_vals:
                    ref_invoice_vals = invoice_vals
                else:
                    ref_invoice_vals['invoice_line_ids'] += invoice_vals[
                        'invoice_line_ids']
                origins.add(invoice_vals['invoice_origin'])
                payment_refs.add(invoice_vals['payment_reference'])
                refs.add(invoice_vals['ref'])
            ref_invoice_vals.update({
                'ref': ', '.join(refs)[:2000],
                'invoice_origin': ', '.join(origins),
                'payment_reference': len(payment_refs) == 1 and \
                payment_refs.pop() or False,
            })
            new_invoice_vals_list.append(ref_invoice_vals)
        invoice_vals_list = new_invoice_vals_list

        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(
                                                default_move_type='in_invoice')
        for vals in invoice_vals_list:
            vals.update({'is_deposit':True})
            moves |= AccountMove.with_company(vals['company_id']).create(vals)
        moves.filtered(lambda m: m.currency_id.round(
            m.amount_total) < 0).action_switch_invoice_into_refund_credit_note()
        return self.action_view_invoice(moves)

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

    def _get_vendor_deposit_reports_values(self, date_range, customer):
        '''return purchase orders on reports (customer filters).'''
        return self.get_orders(date_range, customer)

    def _get_deposit_reports_values(self, date_range):
        '''return All purchase orders on reports.'''
        return self.get_orders(date_range, customer=False)

    def _get_return_value(self):
        '''return total returned amount on report.'''
        return_val = 0
        for line in self.order_line:
            if line.is_deposit_order and line.return_qty:
                return_val += line.return_qty * line.price_unit
        return return_val


class PurchaseOrderLineDeposit(models.Model):
    _inherit = 'purchase.order.line'

    return_qty = fields.Float(string='Return Qty')
    receive_qty = fields.Float(string='Actual Received Qty', readonly=True)
    price_subdeposit = fields.Float(
        string='Return Value', readonly=True, default=0.00)
    deposit_line_id = fields.Many2one(
        'purchase.order.line', string='Deposit Line', ondelete='cascade')
    is_deposit_order = fields.Boolean(
        string='Deposit Order', compute='_set_deposit_order', store=True)
    parent_id = fields.Many2one('purchase.order.line', ondelete='cascade',
        readonly=True)
    price_deposit_total = fields.Float(
        string='Deposit Amount', readonly=True, 
        compute='_set_total_deposit_amount')
    ##container field
    container_line_id = fields.Many2one('purchase.order.line',
        string='Container Line', ondelete='cascade')

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
        '''Shows only Inv done amount on deposit page'''
        for record in self:
            if any(invoice.move_id.move_type == 'in_invoice' and \
                invoice.move_id.state == 'posted' \
                for invoice in record.invoice_lines):
                record.price_deposit_total = record.price_subtotal
            else:
                record.price_deposit_total = float(0.00)

    @api.depends('qty_received_method')
    def _compute_qty_received(self):
        '''it will compute return qty on purchase lines.'''
        res = super(PurchaseOrderLineDeposit, self)._compute_qty_received()
        for line in self:
            qty = receive_qty = 0.00
            outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
            for move in outgoing_moves:
                if move.state != 'done':
                    qty += move.product_uom._compute_quantity(
                            move.product_uom_qty, line.product_uom,
                            rounding_method='HALF-UP')
            for in_move in incoming_moves:
                if in_move.state != 'done':
                    continue
                receive_qty += in_move.product_uom._compute_quantity(
                                in_move.product_uom_qty, line.product_uom,
                                rounding_method='HALF-UP')
            line.write({
                'return_qty':line.return_qty + qty,
                'receive_qty':receive_qty
            })
        return res
