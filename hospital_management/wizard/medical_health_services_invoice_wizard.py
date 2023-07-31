# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime
from odoo.exceptions import UserError

class medical_health_services_invoice(models.TransientModel):
    _name = 'medical.health.service.invoice'
    _description = "Medical Health Service Invoice"

    def create_medical_service_invoice(self):
        active_id = self._context.get('active_id')
        lab_req_obj = self.env['medical.health_service']
        account_invoice_obj  = self.env['account.move']
        account_invoice_line_obj = self.env['account.move.line']
        ir_property_obj = self.env['ir.property']
        lab_req = lab_req_obj.browse(active_id)
        if lab_req.is_invoiced == True:
            raise UserError(_('Already Invoiced'))        
        sale_journals = self.env['account.journal'].sudo().search([('type','=','sale')])
        invoice_vals = {
            'name': self.env['ir.sequence'].next_by_code('medical_health_service_inv_seq'),
            'invoice_origin': lab_req.name or '',
            'move_type': 'out_invoice',
            'ref': False,
            'journal_id':sale_journals and sale_journals[0].id or False ,
            'partner_id': lab_req.patient_id.patient_id.id or False,
            'partner_shipping_id': lab_req.patient_id.patient_id.id,
            'currency_id': lab_req.patient_id.patient_id.currency_id.id ,
            'invoice_payment_term_id': False,
            'fiscal_position_id': lab_req.patient_id.patient_id.property_account_position_id.id,
            'team_id': False,
            'invoice_date': date.today(),
            'company_id': lab_req.patient_id.patient_id.company_id.id or False ,
        }
        res = account_invoice_obj.create(invoice_vals)
        for p_line in lab_req.service_line_ids:
            if p_line.to_invoice == True:
                invoice_line_account_id = False
                
                if lab_req.patient_id.id:
                    invoice_line_account_id = p_line.product_id.property_account_income_id.id or p_line.product_id.categ_id.property_account_income_categ_id.id or False 
                if not invoice_line_account_id:
                    inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
                if not invoice_line_account_id:
                    raise UserError(
                        _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                        (p_line.product_id.name,))
                
                tax_ids = []
                taxes = p_line.product_id.taxes_id.filtered(lambda r: not p_line.product_id.company_id or r.company_id == p_line.product_id.company_id)
                tax_ids = taxes.ids

                invoice_line_vals = {
                    'name': p_line.product_id.name or '',
                    'account_id': invoice_line_account_id,
                    'price_unit':p_line.product_id.lst_price,
                    'product_uom_id': p_line.product_id.uom_id.id,
                    'quantity': 1,
                    'product_id':p_line.product_id.id ,
                }

                res1 = res.write({'invoice_line_ids' :([(0,0,invoice_line_vals)]) })
        if res:
            
            lab_req.write({'is_invoiced': True})
            imd = self.env['ir.model.data']
            action = imd.sudo().xmlid_to_object('account.action_move_out_invoice_type')
            list_view_id = imd.sudo().xmlid_to_res_id('account.view_move_form')
            result = {
                                'name': action.name,
                                'help': action.help,
                                'type': action.type,
                                'views': [ [list_view_id,'form' ]],
                                'target': action.target,
                                'context': action.context,
                                'res_model': action.res_model,
                                'res_id':res.id,
                            }
            if res:
                    result['domain'] = "[('id','=',%s)]" % res.id
                    
        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: