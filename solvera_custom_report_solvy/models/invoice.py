from odoo import fields,models,api,_
from datetime import datetime,date,timedelta
from odoo.exceptions import UserError
from num2words import num2words

class CustomInvoiceModule(models.Model):
    _inherit = "account.move"

    terbilang = fields.Char(string="Terbilangs",compute='Terbilang')
    printing_amount_total = fields.Float(string="Printing Amount Total")
    printing_amount_untaxed = fields.Float(string="Printing Amount Untaxed", compute="get_printing_total")


    def get_printing_total(self):
        total = 0
        for line in self.invoice_line_ids:
            total= total+ line.subtotal_printing_price
        self.printing_amount_untaxed = total


    def Terbilang(self):
        amount_total = int(self.amount_total)
        for this in self:
            this.terbilang = num2words(amount_total, lang='id')+" rupiah"
    

    def write(self,vals):
        temp=0
        
        res = super(CustomInvoiceModule, self).write(vals)
        for i in self:
            for line in i.invoice_line_ids:
                if line.subtotal_printing_price:
                    temp = line.subtotal_printing_price + temp
            if temp != i.amount_total and temp != 0:
                raise UserError(_('Please Check printing Price amount'))
       
        return res
    

    

class CustomInvoiceModuleLine(models.Model):
    _inherit = "account.move.line"


    printing_price = fields.Float(string="Printing Price")
    subtotal_printing_price = fields.Float(string="Sub Total Printing", compute="_get_subtotal_printing_price")

    def _get_subtotal_printing_price(self):
        for i in self:
            sub_total= i.printing_price * i.quantity
            i.subtotal_printing_price = sub_total

    # def write(self,vals):
    #     for i in self:
    #         if i.printing_price:
    #             i.printing_price = vals.get('printing_price') or i.printing_price
    #     res = super(CustomInvoiceModuleLine, self).write(vals)
       
    #     return res

