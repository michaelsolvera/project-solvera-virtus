#-*- coding: utf-8 -*-
#Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
 
from odoo import models, fields, api, _
from datetime import date,datetime
 
class medical_imaging_test_request(models.Model):
     _name = 'medical.imaging.test.request'
     _description = "Medical Imaging Test Request"
     
     name = fields.Char(string="Request",readonly=True,)
     test_date = fields.Datetime(string="Test Date", required = True)
     test_id = fields.Many2one('medical.imaging.test','Test', required = True)
     patient_id = fields.Many2one('medical.patient','Patient', required = True)
     physician_id = fields.Many2one('medical.physician','Physician', required = True)
     urgent = fields.Boolean('Urgent')
     comments = fields.Text(string="Comments")
     state = fields.Selection([
         ('draft', 'Draft'),
         ('confirmed', 'Confirmed'),
         ('done', 'Done'),
         ('cancel', 'Cancel'),
         ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
 
 
     def confirm(self):
         self.write({'state':'confirmed'})
 
     def cancel(self):
         self.write({'state':'cancel'})
 
     @api.model
     def create(self, vals):
         vals['name'] = self.env['ir.sequence'].next_by_code('imaging_seq')
         result = super(medical_imaging_test_request, self).create(vals)
         return result
 
     def done(self):
 
 
         form_obj = self.browse(self.id)
         patient_id = form_obj.patient_id
         physician_id = form_obj.physician_id
         request = form_obj.name
         request_id = self.env['medical.imaging.test.request'].search([('name', '=', request)])
         
         new_created_id_list  = []
         date = form_obj.test_date
         test_ids = form_obj.test_id
         imag_test_req_obj = self.env['medical.imaging.test.result']
         new_created_id = imag_test_req_obj.create({'request_date': date,
                                                             'request_id':form_obj.id,
                                                             'patient_id':patient_id.id,
                                                             'physician_id':physician_id.id,
                                                             'test_id':test_ids.id,
       })
         new_created_id_list.append(new_created_id)
         if new_created_id_list:
             self.write({'state':'done'})
             imd = self.env['ir.model.data']
             action = imd.sudo().xmlid_to_object('hospital_management.action_medical_imaging_test_result')
             list_view_id = imd.sudo().xmlid_to_res_id('hospital_management.medical_imaging_test_result_view')
 
             result = {
                                 'name': action.name,
                                 'help': action.help,
                                 'type': action.type,
                                 'views': [ [list_view_id,'form' ]],
                                 'target': action.target,
                                 'context': action.context,
                                 'res_model': action.res_model,
                                  'res_id':new_created_id.id,
                             }

             return result

