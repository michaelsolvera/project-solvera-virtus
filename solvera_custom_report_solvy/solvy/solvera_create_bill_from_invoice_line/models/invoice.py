from odoo import fields,models,api
from datetime import datetime,date,timedelta
from odoo.exceptions import UserError
from num2words import num2words

class CustomInvoiceModule(models.Model):
    _inherit = "account.move.line"

    move_type = fields.Selection(selection=[
            ('entry', 'Journal Entry'),
            ('out_invoice', 'Customer Invoice'),
            ('out_refund', 'Customer Credit Note'),
            ('in_invoice', 'Vendor Bill'),
            ('in_refund', 'Vendor Credit Note'),
            ('out_receipt', 'Sales Receipt'),
            ('in_receipt', 'Purchase Receipt'),
        ], string='Type', required=True, store=True, index=True, readonly=True, tracking=True,
        default="entry", change_default=True, related="move_id.move_type")
    
    state_bill = fields.Selection(selection=[
            ('ready', 'Ready'),
            ('create', 'Created'),
        ], string='Type', required=True, store=True, index=True, readonly=True, tracking=True,
        default="ready", change_default=True)
    def create_bill_vendor(self):
        today= date.today()
        bill_obj = self.env['account.move']
        for i in self:
            invoice_line = [
                    (0, 0, {
                        'product_id':i.product_id.id,
                        'name':i.product_id.display_name,
                        'account_id':i.product_id.categ_id.property_account_expense_categ_id.id,
                        'quantity':i.quantity,
                        'price_unit':i.product_id.standard_price,
                        'tax_ids':i.tax_ids.ids,



                    }),
                    
                    ]
            bill_obj.create({
                'move_type':'in_invoice',
                'partner_id':i.product_id.partner_id,
                'ref':i.move_id.name+' - '+i.name,
                'invoice_date': today,
                'invoice_line_ids':invoice_line

            })
            i.write({'state_bill': 'create'})

    

 