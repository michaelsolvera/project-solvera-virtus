# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from datetime import datetime
from calendar import monthrange
from odoo import models, fields


class SaleReportWz(models.TransientModel):
    _name = 'sale.report.wz'
    _description = 'Sales Deposit Report Wizard'

    customer_ids = fields.Many2many('res.partner', string='Customer(s)')
    from_date = fields.Date(
        string='From Date', default=lambda *a: fields.Datetime.to_string(
            fields.Datetime.now()))
    to_date = fields.Date(
        string='To Date', default=lambda *a: fields.Datetime.to_string(
            fields.Datetime.now().replace(day = monthrange(
                datetime.now().year, datetime.now().month)[1])))
    quartly_option = fields.Selection([
        ('jan','January-March'),
        ('apr','April-June'),
        ('july','July-Septmber'),
        ('oct','October-december')], string='Select Quater', default='jan')
    hlf_year_option = fields.Selection([
        ('jan','January-June'),
        ('july','July-December')], string="Select Half Year", default='jan')
    by_periods = fields.Selection([
        ('d','Daily'),
        ('m','Monthly'),
        ('q','Quartley'),
        ('h','Half Yearly'),
        ('y','Yearly')], string='By Period', default='m')
    year = fields.Selection([(str(num), str(num)) for num in range( ((
        datetime.now().year)-10),((datetime.now().year)+1) )], string='Year(s)')
    by_type = fields.Selection([('all', 'All'), ('customer', 'Customer')], 
        default='all', string='Type')

    def print_self_report(self):
        self.ensure_one()
        datas = {
            'ids': self.customer_ids.ids,
            'model': 'sale.order',
            'form': self.read(),
            'docs': self,
        }
        return self.env.ref(
            'cit_deposit_management.report_sale_deposit').with_context(
            allowed_company_ids=self.env.context.get('allowed_company_ids')
            ).report_action(self,data=datas)
