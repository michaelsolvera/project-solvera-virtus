# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools # type: ignore
from odoo.exceptions import Warning


class ACcountMove(models.Model):
    _inherit = 'account.move'

    service_type_id = fields.Many2one('service.type', string='Service Type', required=True)
    attachment = fields.Binary(string="PNR Attachment")
    file_name = fields.Char('File Name')
    pnr = fields.Char(string='PNR', unique=True, required=True)
    ticket_no = fields.Char(string='Ticket No.')
    passenger_name = fields.Html(string='Passenger Name', sanitize=False, strip_style=False, strip_classes=False)
    from_id = fields.Many2one('location.master', string='From')
    to_id = fields.Many2one('location.master', string='To')
    departure_date = fields.Date(string='Departure Date')
    issued_through = fields.Many2many('res.partner', string='Issued Through', domain=[('supplier_rank', '>', 0)])
    agent_id = fields.Many2many('agent.master', string='Agent')
    pos_machine_ids = fields.One2many('pos.machine.lines', 'line_id', string='POS Machine')
    profit_sum = fields.Float('Profit', compute='_compute_total_profit', store=True)
    pos_amount_total = fields.Float('Amount Total', compute='_compute_amount_total', store=True)


    @api.depends('pos_machine_ids.amount')
    def _compute_amount_total(self):
        for order in self:
            order.pos_amount_total = sum(order.pos_machine_ids.mapped('amount'))
    
    @api.depends('invoice_line_ids.profit')
    def _compute_total_profit(self):
        for order in self:
            order.profit_sum = sum(order.invoice_line_ids.mapped('profit'))

    

    def action_post(self):
        res = super(ACcountMove, self).action_post()
        return res
    

    _sql_constraints = [
        ('unique_pnr', 'unique(pnr)', 'The PNR must be unique!'),
    ]


class ACcountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cost_value = fields.Float('Cost')
    profit = fields.Float('Profit')

    @api.onchange('cost_value','price_subtotal')
    def _onchange_cost_and_subtotal(self):
        self.profit = self.price_subtotal - self.cost_value


class PosMachineLines(models.Model):
    _name = 'pos.machine.lines'
    _description = 'pos machine lines'

    line_id = fields.Many2one('account.move', string='Move ID')

    # currency_id = fields.Many2one('res.currency', string='Currency')
    # type_selection = fields.Selection([('card', 'Card'),('cash', 'Cash')], string='Type')
    # card_no = fields.Char('Card No.')
    # bank_id = fields.Many2one('res.bank', string='Bank')
    authentication_code = fields.Char('Authentication Code')
    amount = fields.Float('Amount')
    