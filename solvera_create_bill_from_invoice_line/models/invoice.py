from odoo import fields,models,api
from datetime import datetime,date,timedelta
from odoo.exceptions import UserError
from num2words import num2words

class CustomInvoiceModule(models.Model):
    _inherit = "account.move"

    invoice_bill_ids = fields.Many2many('account.move',"related_invoice_rel","related_bill_rel","related_move_id" , string="Invocie ID", copy=False)
    invoice_bill_count = fields.Integer(string="Count", copy=False)

    def action_view_bill(self):
        action = self.env.ref('account.action_move_out_invoice_type')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        result['domain'] = [('invoice_bill_ids', '=', self.id)]
        pick_ids = sum([self.invoice_bill_ids.id])
        if pick_ids:
            res = self.env.ref('account.view_move_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids or False
        return result


    # def action_view_bill(self):
    #     self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
    #     action = self.env.ref('stock.action_picking_tree_ready')
    #     result = action.read()[0]
    #     result.pop('id', None)
    #     result['context'] = {}
    #     result['domain'] = [('id', '=', self.invoice_picking_id.id)]
    #     pick_ids = sum([self.invoice_picking_id.id])
    #     if pick_ids:
    #         res = self.env.ref('stock.view_picking_form', False)
    #         result['views'] = [(res and res.id or False, 'form')]
    #         result['res_id'] = pick_ids or False
    #     return result
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
        tax_parameter = False

        for i in self:
            if i.tax_ids:
                tax_parameter = self.company_id.account_purchase_tax_id
            invoice_line = [
                    (0, 0, {
                        'product_id':i.product_id.id,
                        'name':i.product_id.display_name,
                        'account_id':i.product_id.categ_id.property_account_expense_categ_id.id,
                        'quantity':i.quantity,
                        'price_unit':i.product_id.standard_price,
                        'tax_ids':tax_parameter,

                    }),
                    
                    ]
            create_bill = bill_obj.create({
                'move_type':'in_invoice',
                'partner_id':i.product_id.partner_id,
                'ref':i.move_id.name+' - '+i.name,
                'invoice_date': today,
                'invoice_line_ids':invoice_line,
                'invoice_bill_ids':[0,0,i.move_id._origin.id],

            })
            i.write({'state_bill': 'create'})
                

    

 