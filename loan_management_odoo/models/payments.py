from odoo import models, fields, api

class payments(models.Model):
    _name = 'payment.borrower'
    _rec_name = 'payee'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'paid_date'
    _description = "Borrower's payments"

    
    loan_number = fields.Char(string="Loan no")
    payee = fields.Many2one('borrower.borrower', string="Borrower")
    paid_amount = fields.Float(string="Amount")
    paid_date = fields.Datetime(string="Collected date", required=False, default=lambda self: fields.datetime.now())
    method = fields.Selection([
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('bank', 'Bank'),
        ('online', 'Online Transfer'),
    ], string="Method")
    collected_by = fields.Many2one('hr.employee', string="Collected by")
    description = fields.Text(string="Description")
    receipt = fields.Boolean(string="Receipt")