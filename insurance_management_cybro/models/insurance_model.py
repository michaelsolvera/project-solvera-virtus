# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta,date


class InsuranceDetails(models.Model):
    _name = 'insurance.details'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Travel Agent', required=True,domain="[('travel_agent_boolean', '=', True)]")
    pax_name_id = fields.Many2one('res.partner', string='Name', required=True,domain="[('parent_id', '=', partner_id)]")
    date_start = fields.Date(string='Date Started', default=fields.Date.today(), required=True)
    close_date = fields.Date(string='Date Closed')
    invoice_ids = fields.One2many('account.move', 'insurance_id', string='Invoices', readonly=True)
    bill_ids = fields.One2many('account.move', 'bill_id', string='Vendor Bill', readonly=True)
    employee_id = fields.Many2one('employee.details', string='User Agency', required=True)
    commission_rate = fields.Float(string='Commission Percentage')
    policy_id = fields.Many2one('policy.details', string='Product', required=True)
    amount = fields.Float(related='policy_id.amount', string='Rupiah Net')
    amount_rate = fields.Float(string='Rate IDR')
    discount_agent = fields.Float(string='Diskon Agen')
    extra_discount = fields.Float(string='Extra Discount')
    inv_gtass = fields.Char(string='INV GTASS')
    discount_beneficiary = fields.Char(string='Extra Discount Beneficiary')
    polis_amount = fields.Float(related='policy_id.polis_amount', string='Amount')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('closed', 'Closed')],
                             required=True, default='draft')
    hide_inv_button = fields.Boolean(copy=False)
    note_field = fields.Html(string='Comment')

    @api.onchange('date_start','policy_id')
    def input_close_date(self):
        for i in self:
            if i.date_start:
                i.close_date = i.date_start + timedelta(days=i.policy_id.policy_duration)


    def confirm_insurance(self):
        if self.amount > 0:
            self.state = 'confirmed'
            self.hide_inv_button = True
        else:
            raise UserError(_("Amount should be Greater than Zero"))


    def create_invoice(self):
        today=date.today()
        if self.discount_agent:
            move_lines = [
                    (0, 0, {
                        'account_id':self.policy_id.insurace_discount_journal_id.id,
                        'name': 'Agent Discount',
                        'debit':self.discount_agent,
                    }),
                    ]
            diff_price = self.amount - self.discount_agent
            created_invoice=self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.partner_id.id,
                'invoice_user_id': self.env.user.id,
                'invoice_origin': self.name,
                'invoice_line_ids': [(0, 0, {
                    'name': 'Invoice For Insurance',
                    'quantity': 1,
                    'price_unit': self.amount,
                    'account_id': self.policy_id.insurace_journal_id.id,
                })],
            })
            self.invoice_ids = created_invoice
            for line in self.invoice_ids.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                                                'debit':diff_price,
                                            })
            created_invoice.with_context(check_move_validity=False).write({
                'line_ids' : move_lines
            })
                
        else:
            created_invoice=self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.partner_id.id,
                'invoice_user_id': self.env.user.id,
                'invoice_origin': self.name,
                'invoice_line_ids': [(0, 0, {
                    'name': 'Invoice For Insurance',
                    'quantity': 1,
                    'price_unit': self.amount,
                    'account_id': self.policy_id.insurace_journal_id.id,
                })],
            })
            self.invoice_ids = created_invoice




        created_bill=self.env['account.move'].create({
            'move_type': 'in_invoice',
            'invoice_date':today,
            'partner_id': self.partner_id.id,
            'invoice_user_id': self.env.user.id,
            'invoice_origin': self.name,
            'invoice_line_ids': [(0, 0, {
                'name': 'Bill For Travel Agent',
                'quantity': 1,
                'price_unit': self.extra_discount,
                'account_id': self.policy_id.bill_agent_journal_id.id,
            })],
        })
        self.bill_ids = created_bill
        if self.policy_id.payment_type == 'fixed':
            self.hide_inv_button = False

    def close_insurance(self):
        for records in self.invoice_ids:
            if records.state == 'paid':
                raise UserError(_("All invoices must be Paid"))
        self.state = 'closed'
        self.hide_inv_button = False

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('insurance.details') or 'New'
        return super(InsuranceDetails, self).create(vals)


class AccountInvoiceRelate(models.Model):
    _inherit = 'account.move'

    insurance_id = fields.Many2one('insurance.details', string='Insurance')
    bill_id = fields.Many2one('insurance.details', string='bill')
    claim_id = fields.Many2one('claim.details', string='Insurance')