# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime

class wizard_multiple_test_request(models.TransientModel):
    _name = 'wizard.multiple.test.request'
    _description = "Wizard Multiple Test Request"

    request_date = fields.Datetime('Request Date', required = True)
    wizard_multiple_test_patient_id =  fields.Many2one('medical.patient','Patient', required = True)
    urgent =  fields.Boolean('Urgent',)
    wizard_multiple_test_physician_id = fields.Many2one('medical.physician','Doctor', required = True)
    wizard_multiple_test_owner_partner_id  = fields.Many2one('res.partner','Owner')
    tests_ids = fields.Many2many('medical.test_type', 
            'lab_test_report_test_rel', 'test_id', 'report_id', 'Tests')

    def create_lab_test(self):
        wizard_obj = self

        patient_id = wizard_obj.wizard_multiple_test_patient_id
        phy_id = wizard_obj.wizard_multiple_test_physician_id
        new_created_id_list  = []
        date = wizard_obj.request_date 
        for test_id in wizard_obj.tests_ids:
            lab_test_req_obj = self.env['medical.test_type']
            test_browse_record = lab_test_req_obj.browse(test_id.id)
            test_name = test_browse_record.name
            medical_test_request_obj  = self.env['medical.patient.lab.test']
            new_created_id = medical_test_request_obj.create({'date': date,
                                                        'doctor_id': phy_id.id,
                                                        'patient_id':patient_id.id,
                                                        'state': 'tested',
                                                        'name':test_id.id,
                                                        
                                                        'request' :self.env['ir.sequence'].next_by_code('test_seq')
      })

            new_created_id_list.append(new_created_id.id)
        if new_created_id_list:                     
            imd = self.env['ir.model.data']
            action = imd.sudo().xmlid_to_object('hospital_management.action_medical_patient_lab_test')
            list_view_id = imd.sudo().xmlid_to_res_id('hospital_management.medical_patient_lab_test_tree_view')

            result = {
                                'name': action.name,
                                'help': action.help,
                                'type': action.type,
                                'views': [ [list_view_id,'tree' ]],
                                'target': action.target,
                                'context': action.context,
                                'res_model': action.res_model,
                            }
            
            if len(new_created_id_list)  :
                        result['domain'] = "[('id','in',%s)]" % new_created_id_list
            return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    