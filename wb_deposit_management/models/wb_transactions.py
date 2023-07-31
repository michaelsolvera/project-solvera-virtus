from odoo import api, fields, models, _
from odoo.exceptions import UserError

class WbBankTransactions(models.Model):
    _name = "wb.bank.transactions"
    _description = "Weblearns Bank Transactions Model"

    name = fields.Many2one("res.partner", string="Customer", required=True)
    bank_id = fields.Many2one("wb.bank", string="Bank", required=True,
                              default=lambda lm:lm.env.user.wb_bank_id.id)
    balance = fields.Float("Balance")
    remarks = fields.Char("Remarks")
    state = fields.Selection([('draft','Draft'), ('done','Done')],
                             string="State", default='draft')
    tran_state = fields.Selection([('deposit', 'Deposit'),
                                   ('withdraw', 'Withdraw'),
                                   ('admin', 'Administrator Fee')],
                                  string="Transaction Status", default='deposit', required=True)
    final_balance = fields.Float("Final Balance", compute="_get_final_balance")

    def _get_final_balance(self):
        for record in self:
            if record.state == "done":
                if record.tran_state == "withdraw" or record.tran_state == "admin" :
                    record.final_balance = -(record.balance)
                else:
                    record.final_balance = record.balance
            else:
                record.final_balance =0.0

    def transaction_done(self):
        if self.tran_state == 'withdraw' and self.name.balance < self.balance:
            raise UserError(_("You don't have enough amount to withdraw."))
        self.state = 'done'
        self.env.ref("wb_deposit_management.bank_transaction_done_email_template").send_mail(self.id, force_send=False)

    def generate_interest(self):
        partner_obj= self.env['res.partner'].search([])
        trans_obj= self.env['wb.bank.transactions']
        print('yesbisas')

        for partner in partner_obj:
            print("test_fungtion",partner.name)
            if partner.wb_bank_id:
                if partner.balance > 0:
                    print("test_fungtion",partner.name)
                    trans_id=trans_obj.create({
                        'name': partner.id,
                        'bank_id': partner.wb_bank_id.id,
                        'balance':((partner.wb_bank_id.interest_value/100)/12)*partner.balance,
                        'remarks': 'Montly Interest',
                        'tran_state':'deposit'
                    })
                    trans_id.transaction_done()
    def generate_admin(self):
        partner_obj= self.env['res.partner'].search([])
        trans_obj= self.env['wb.bank.transactions']
        for partner in partner_obj:
            if partner.wb_bank_id:
                if partner.balance > 0:
                    trans_id=trans_obj.create({
                        'name': partner.id,
                        'bank_id': partner.wb_bank_id.id,
                        'balance':partner.wb_bank_id.fee_value,
                        'remarks': 'Montly Interest',
                        'tran_state':'admin'
                    })
                    trans_id.transaction_done()
