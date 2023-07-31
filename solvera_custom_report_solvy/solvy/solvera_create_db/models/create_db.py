
from calendar import month
from itertools import product
import logging
from xendit import Xendit
import subprocess
import requests
import os
import tempfile
from tempfile import mkstemp
from datetime import datetime,timedelta
import datetime
from shutil import move
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'
    packet = fields.Selection([
        ('1', 'Lite'),
        ('2', 'Advance'),
        ('3','Profesional')
    ], string='Packet')
    db = fields.Char(string='Database')
    pw = fields.Char(string='Password User')
    time_request=fields.Datetime(string='Date Time Request')
    time_verification = fields.Datetime(string='Date Time Verification')
    token = fields.Char(string="token")
    exp_date = fields.Datetime(string='Expired Date')
    virtual_account = fields.Char(sting="Nomor VA")
    id_va = fields.Char(sting="id")
    status_member = fields.Selection([
        ('3', '3 Bulan'),
        ('12', '1 Tahun'),
        ('24','2 Tahun')
    ], string='status member')
    invoice_url=fields.Char(string="invoice_url")
    invoice_id=fields.Char(string="invoice_id")
    status_payment = fields.Selection([
        ('1', 'Paid'),
        ('0', 'Not Paid'),
    ], string='status payment')
    
    def send_email(self,*get):
        partner=get
        # obj_id=self.env['res.partner'].search([(partner, '=', 'id' )])
        for i in get:
            template_id = self.env.ref('solvera_create_db.reg_email')
            template_id.send_mail(partner[0],force_send=True)
        print(partner,'berhasil_kirim')
        return True
    
    def send_change_password(self,*get):
        partner=get
        # obj_id=self.env['res.partner'].search([(partner, '=', 'id' )])
        for i in get:
            template_id = self.env.ref('solvera_create_db.change_pass_email')
            template_id.send_mail(partner[0],force_send=True)
        return True

    @api.onchange('status_member')
    def payment_extention(self):

        temp=self.exp_date
        for i in self:
            if i.exp_date:
                if i.status_member == '3':
                    exp = i.exp_date + relativedelta(months=6)       
                elif i.status_member == '12':
                    exp = i.exp_date + relativedelta(years=1)           
                elif i.status_member == '24':
                    exp = i.exp_date + relativedelta(years=2)                
                else:
                    exp = temp
                i.write({'exp_date': exp})
    # @api.onchange('exp_date')
    def exp_db(self):
        for this in self:
            if this.exp_date:
                today = datetime.now()
                if this.exp_date == today:
                    return {
            'type': 'ir.actions.act_url',
            'url': '/web/db_lock?db=%s' % self.db,
            'target': 'self',
            'res_id': self.id,
        }

    def unlock(self):
        for this in self:
            if this.exp_date:
                today = datetime.datetime.now()
                if this.exp_date == today:
                   
                    return {
            'type': 'ir.actions.act_url',
            'url': '/web/db_unlock?db=%s' % self.db,
            'target': 'self',
            'res_id': self.id,
                    }
    def generate_va(self):
        print(str(self.name),"test_print")
        
        api_key = "xnd_development_3uzESw7LPejhIz0UOsWh68eGRC3mjrbgiOHl1XCHWZUHi75eQ9nwu0zdcShw8A"
        xendit_instance = Xendit(api_key=api_key)
        VirtualAccount = xendit_instance.VirtualAccount
        va_name = self.name
        today = datetime.datetime.now()
        ts= today.timestamp()

        virtual_account = VirtualAccount.create(
            external_id = "VA_fixed-"+str(ts),
            bank_code = "BRI",
            name = va_name,
        )
        dict_contact = []
        dict_contact.append(virtual_account)

        for this in dict_contact:
            self.write({
                'virtual_account': this.account_number,
                'id_va' : this.id,
            })
            
        
        return virtual_account

    def create_invoice(self):
        account_obj = self.env['account.move']
        account_line_obj =self.env['account.move.line']
        today=datetime.date.today()

        vals_line = []

        for this in self:
            if this.status_member == '3':
                product_obj = self.env['product.product'].search([('name','=','Paket A')])
                vals_line.append({
                    'product_id': product_obj.id,
                    'name': product_obj.name,
                    'price_unit':product_obj.lst_price
                })
        for i in self:
            partner_obj=self.env['res.partner'].search([('db','=',self.db)])
            account_obj.create({
                'partner_id':partner_obj[0],
                'move_type' : 'out_invoice',
                'invoice_date': today,
                'payment_reference':self.id_va,
                'invoice_line_ids':vals_line,
            })
        account_obj.action_post()

    def create_xendit_invoice(self):
        api_key = "xnd_development_3uzESw7LPejhIz0UOsWh68eGRC3mjrbgiOHl1XCHWZUHi75eQ9nwu0zdcShw8A"
        xendit_instance = Xendit(api_key=api_key)
        Invoice = xendit_instance.Invoice
        today = datetime.now()
        ts= today.timestamp()
        customer = {
            'given_names': self.name,
            'email': self.email,
            'mobile_number': self.mobile,
        }

        invoice = Invoice.create(
            external_id="invoice"+str(ts),
            amount=20000,
            description="Invoice Demo #123",
            invoice_duration=86400,
            customer = customer,
            currency  = "IDR",  
            payer_email =self.email,
        )
        dict_invoice = []
        dict_invoice.append(invoice)

        for this in dict_invoice:
            self.write({
                'invoice_id': this.id,
                'status_payment':'0',
            })

    def get_invoice(self):
        api_key = "xnd_development_3uzESw7LPejhIz0UOsWh68eGRC3mjrbgiOHl1XCHWZUHi75eQ9nwu0zdcShw8A"
        xendit_instance = Xendit(api_key=api_key)
        Invoice = xendit_instance.Invoice

        invoice = Invoice.get(
            invoice_id=self.invoice_id,
        )
        dict_get_invoice = []
        dict_get_invoice.append(invoice)

        for this in dict_get_invoice:
            self.write({
                'invoice_url': this.invoice_url,
                'status_payment':'0',
            })


    @api.onchange('exp_date')
    def warning_payment(self):
        
        if self.exp_date:
            has_exp = self.exp_date - timedelta(days=3)
            today=datetime.now()
            if today == has_exp:
                self.create_invoice()
                self.create_xendit_invoice()
                self.get_invoice()
    def paid(self):
        self.write({
                'status_payment': "1"
            })

            

        