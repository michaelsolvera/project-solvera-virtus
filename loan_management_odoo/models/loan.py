from odoo import models, fields, api

class loan_duration(models.Model):
    _name = 'loan.duration'

    name = fields.Char("Loan Duration Name", compute="_compute_duration_name" )
    duration = fields.Integer("Loan Duration", required=True)
    duration_type = fields.Selection([
        ('months', 'Months'),
        ('years', 'Years')
    ], string="Duration Type" , required=True, default="years")

    @api.depends('duration', 'duration_type')
    def _compute_duration_name(self):
        for rec in self:
            rec.name = str(rec.duration) + " " + rec.duration_type
            

class loan(models.Model):
    _name = 'loans.loans'
    _rec_name = 'borrower'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'loan_date'
    _description = 'Loan Informations'

    borrower = fields.Many2one('borrower.borrower', string="Borrower name", required=True, stored=True)
    loan_type = fields.Selection([
        ('business', 'Business loan'),
        ('personal', 'Personal loan'),
        ('house', 'House Finance loan'),
        ('student', 'Student loan'),
        ('pensioner', 'Pensioner loan'),
    ], required=True, string="Loan type")
    loan_no = fields.Char(string="Loan no")
    loan_date = fields.Datetime(string="Loan date", required=False, default=lambda self: fields.datetime.now())
    disbursed_by = fields.Selection([
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('bank', 'Bank'),
        ('online', 'Online Transfer'),
    ], string="Disbursed by")
    amount = fields.Float(string="Principal", required=True)
    interest_method = fields.Selection([
        ('interest_rate', 'Interest Rate'),
        ('compound_interest', 'Compound Interest'),
        ('interest_only', 'Interest only')
    ], string="Interest method")
    interest_type = fields.Selection([
        ('percentage_based', 'Percentage based'),
        ('fixed_amount', 'Fixed amount'),
    ], string="Interest type")
    interest_percentage = fields.Float(string="Interest Rate(%)", required=False)
    interest_amount = fields.Float(string="Loan interest(amount)", required=False)
    loan_duration = fields.Integer("Period(Months)")
    loan_period = fields.Many2one('loan.duration')
    #amount_to_repaid
    repayment = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Biweekly'),
        ('monthly', 'Monthly'),
        ('bimonthly', 'Bimonthly'),
        ('quarterly', 'Quarterly'),
        ('every4month', 'Every 4 months'),
        ('semi_annual', 'Semi-Annual'),
        ('yearly', 'Yearly'),
    ], string="Repayment Cycle")
    loan_status = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('processing', 'Processing'),
        ('pending', 'Pending'),
        ('denied', 'Denied'),
        ('approved', 'Approved'),
    ], default="draft", string="Loan status")

    #Payment
    payment_status = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    ], string="Pay status", default="not_paid")
    payable_amount = fields.Float(string="Total Loan")
    paid_amount = fields.Float(string="Paid")
    remaining_amount = fields.Float(string="Due")
    guarantor = fields.Many2one('borrower.borrower', string="Guarantor", required=False)
    loan_file = fields.Binary(string="Loan file")
    description = fields.Text(string="Description")
    loan_officer = fields.Many2one('hr.employee', string="Loan Officer")

    montlyPayment = fields.Float("Monthly Payment", compute="_calculate_interest")
    total_loan_amount = fields.Float("Total Loan Amount", compute="_calculate_interest")
    total_interest_amount = fields.Float("Total Interest Amount", compute="_calculate_interest")

    @api.depends('amount', 'interest_percentage', 'loan_duration')
    def _calculate_interest(self):
        total_loan_amount = 0
        total_interest_amount = 0
        principal_amount = self.amount
        rate = self.interest_percentage / (12 * 100)
        time = self.loan_duration
        mia = self.montlyPayment
        if time > 0:
            mia = (principal_amount * rate * pow(1 + rate , time)) / (pow(1 + rate, time) - 1)
        self.montlyPayment = mia
        self.total_loan_amount = mia * time
        self.total_interest_amount = self.total_loan_amount - principal_amount