# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from calendar import monthrange
from collections import OrderedDict
from odoo import models, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ReportSaleDeposit(models.AbstractModel):
    _name = 'report.cit_deposit_management.sale_deposit_template'
    _description = 'Sales Deposit Report Template'

    def months_between(self, start, end):
        months = []
        cursor = datetime.strptime(str(start), DEFAULT_SERVER_DATE_FORMAT)
        while cursor < datetime.strptime(str(end), DEFAULT_SERVER_DATE_FORMAT):
            if cursor.month not in months:
                months.append((str(cursor.year)+'-'+str(cursor.month)+'-01', str(
                    cursor.year)+'-'+ str(cursor.month)+'-'+str(
                    monthrange(cursor.year, cursor.month)[1])))
            cursor += timedelta(weeks=1)
        return OrderedDict((m, True) for m in months).keys()

    def days_between(self, start, end):
        days = []
        cursor = datetime.strptime(str(start), DEFAULT_SERVER_DATE_FORMAT)
        while cursor <= datetime.strptime(str(end), DEFAULT_SERVER_DATE_FORMAT):
            if cursor.month not in days:
                days.append((str(cursor.year)+'-'+str(cursor.month)+'-'+str(
                    cursor.day), str(cursor.year)+'-'+str(cursor.month)+'-'+str(
                    cursor.day)))
            cursor += timedelta(days=1)
        return OrderedDict((m, True) for m in days).keys()

    @api.model
    def _get_report_values(self, docids, data=None):
        Report = self.env['ir.actions.report']._get_report_from_name(
            'cit_deposit_management.sale_deposit_template')
        fromdate = todate = False
        year = data['form'][0].get('year', False)
        quartly_option = data['form'][0].get('quartly_option', False)
        hlf_year_option = data['form'][0].get('hlf_year_option', False)
        if not data['form'][0].get('by_periods') == 'd':
            if data['form'][0].get('by_periods') == 'y' and year:
                fromdate = str(year)+'-01-01'
                todate = str(year)+'-12-31'
                data['form'][0].update({'from_date':fromdate,'to_date':todate})

            elif data['form'][0].get('by_periods') == 'q' and quartly_option and year:
                if quartly_option == 'jan':
                    fromdate = str(year)+'-01-01'
                    todate = str(year)+'-03-31'
                elif quartly_option == 'apr':
                    fromdate = str(year)+'-04-01'
                    todate = str(year)+'-06-30'
                elif quartly_option == 'july':
                    fromdate = str(year)+'-07-01'
                    todate = str(year)+'-09-30'
                else:
                    fromdate = str(year)+'-10-01'
                    todate = str(year)+'-12-31'

                data['form'][0].update({'from_date':fromdate,'to_date':todate})

            elif data['form'][0].get('by_periods') == 'h' and hlf_year_option and year:
                if hlf_year_option == 'jan':
                    fromdate = str(year)+'-01-01'
                    todate = str(year)+'-06-30'
                else:
                    fromdate = str(year)+'-07-01'
                    todate = str(year)+'-12-31'
                data['form'][0].update({'from_date':fromdate,'to_date':todate})

            else:
                fromdate = data['form'][0].get('from_date', False)
                todate = data['form'][0].get('to_date', False)
            monthlist = self.months_between(fromdate, todate) if fromdate and \
                todate else []
        else:
            fromdate = data['form'][0].get('from_date', False)
            todate = data['form'][0].get('to_date', False)
            monthlist = self.days_between(fromdate, todate) if fromdate and \
                todate else []

        docargs = {
            'doc_ids': data['form'][0]['customer_ids'],
            'doc_model': Report.model,
            'docs': self.env['sale.report.wz'].browse(data['form'][0]['id']),
            'form':data['form'][0],
            'monthlist':monthlist,
        }
        return docargs
