
from tempfile import mkstemp
from xendit import Xendit
from shutil import move
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta,date

class TempPartner(models.Model):
    _inherit = 'res.partner'
   
    exp_date = fields.Datetime(string='Expired Date')
    virtual_account = fields.Char(srting="Nomor VA")
    id_va = fields.Char(string="id")
    status_member = fields.Selection([
        ('1', '1 Bulan'),
        ('2','1 Tahun')
    ], string='status member')
    invoice_url=fields.Char(string="invoice_url")
    invoice_id=fields.Char(string="invoice_id")
    status_payment = fields.Selection([
        ('1', 'Paid'),
        ('0', 'Not Paid'),
    ], string='status payment')

    def add_month(self):
        if self.exp_date:
            for i in self:
                exp = i.exp_date + relativedelta(months=1)
                i.write({
                'exp_date': exp,
            })


    def add_year(self):
        if self.exp_date:
            for i in self:
                exp = i.exp_date + relativedelta(years=1)
                i.write({
                'exp_date': exp,
            })



    # @api.onchange('exp_date')
    def exp_db(self):
        today = date.today()
        exp_obj= self.env['res.partner'].search([('exp_date','=',today)])
        for exp in exp_obj:
            return {
        'type': 'ir.actions.act_url',
        'url': '/web/db_lock?db=%s' % exp.db,
        'target': 'self',
        'res_id': exp.id,
        }

    def unlock(self):
        for this in self:
            # if this.exp_date:
            #     today = datetime.now()
            #     if this.exp_date == today:
            return {
            'type': 'ir.actions.act_url',
            'url': '/web/db_unlock?db=%s' % self.db,
            'target': 'self',
            'res_id': this.id,
            }
    def generate_va(self):
        print(str(self.name),"test_print")
        
        api_key = "xnd_development_3uzESw7LPejhIz0UOsWh68eGRC3mjrbgiOHl1XCHWZUHi75eQ9nwu0zdcShw8A"
        xendit_instance = Xendit(api_key=api_key)
        VirtualAccount = xendit_instance.VirtualAccount
        va_name = self.name
        today = datetime.now()
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
        today=datetime.today()

        vals_line = []

        for this in self:
            if this.status_member == '1':
                if this.packet == '1':
                    product_obj = self.env['product.product'].search([('default_code','=','TR1')])
                    vals_line.append({
                        'product_id': product_obj.id,
                        'name': product_obj.name,
                        'price_unit':product_obj.lst_price
                    })
                elif this.packet == '2':
                    product_obj = self.env['product.product'].search([('default_code','=','CF1')])
                    vals_line.append({
                        'product_id': product_obj.id,
                        'name': product_obj.name,
                        'price_unit':product_obj.lst_price
                    })
                elif this.packet == '3':
                    product_obj = self.env['product.product'].search([('default_code','=','HO1')])
                    vals_line.append({
                        'product_id': product_obj.id,
                        'name': product_obj.name,
                        'price_unit':product_obj.lst_price
                    })
            if this.status_member == '2':
                if this.packet == '1':
                    product_obj = self.env['product.product'].search([('default_code','=','TR12')])
                    vals_line.append({
                        'product_id': product_obj.id,
                        'name': product_obj.name,
                        'price_unit':product_obj.lst_price
                    })
                elif this.packet == '2':
                    product_obj = self.env['product.product'].search([('default_code','=','CF12')])
                    vals_line.append({
                        'product_id': product_obj.id,
                        'name': product_obj.name,
                        'price_unit':product_obj.lst_price
                    })
                elif this.packet == '3':
                    product_obj = self.env['product.product'].search([('default_code','=','HO12')])
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
                'payment_reference':self.invoice_id,
                'invoice_line_ids':vals_line,
            })
        account_search = self.env['account.move'].search([('payment_reference','=',self.invoice_id)])
        account_search.action_post()

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
        ##packet toko retail
        if self.packet == "1":
            if self.status_member == '1':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=199000,
                    description="Invoice Retail Bulanan#"+str(self.name),
                    invoice_duration=259200,
                    customer = customer,
                    currency  = "IDR",  
                    payer_email =self.email,
                )
                dict_invoice = []
                dict_invoice.append(invoice)
            if self.status_member == '2':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=1990000,
                    description="Invoice Retail Tahunan#"+str(self.name),
                    invoice_duration=259200,
                    customer = customer,
                    currency  = "IDR",  
                    payer_email =self.email,
                )
                dict_invoice = []
                dict_invoice.append(invoice)

        ##packet Resto
        elif self.packet == "2":
            if self.status_member == '1':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=399000,
                    description="Invoice Retail Cafe & Resto Bulanan#"+str(self.name),
                    invoice_duration=259200,
                    customer = customer,
                    currency  = "IDR",  
                    payer_email =self.email,
                )
                dict_invoice = []
                dict_invoice.append(invoice)
            if self.status_member == '2':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=3990000,
                    description="Invoice Retail Cafe & Resto Tahunan#"+str(self.name),
                    invoice_duration=259200,
                    customer = customer,
                    currency  = "IDR",  
                    payer_email =self.email,
                )
                dict_invoice = []
                dict_invoice.append(invoice)

        ##packet Hotel
        elif self.packet == "3":
            if self.status_member == '1':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=599000,
                    description="Invoice Retail Hotel Bulanan#"+str(self.name),
                    invoice_duration=259200,
                    customer = customer,
                    currency  = "IDR",  
                    payer_email =self.email,
                )
                dict_invoice = []
                dict_invoice.append(invoice)
            if self.status_member == '1':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=5990000,
                    description="Invoice Retail Hotel Tahunan#"+str(self.name),
                    invoice_duration=259200,
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
                'status_payment': "0",
            })



    def warning_payment(self):
        todays=date.today()
        has_exp = todays + timedelta(days=3)
        exp_obj= self.env['res.partner'].search([('exp_date','=',has_exp)])
        for this in exp_obj:
            this.create_xendit_invoice()
            this.get_invoice()
            this.create_invoice()
    @api.onchange('status_payment')
    def regpaid(self):
        account_search = self.env['account.move'].search([('payment_reference','=',self.invoice_id)])
        today =datetime.now()
        wizard = self.env['account.payment.register'].with_context(
                active_model = 'account.move',
                active_ids = account_search.ids,
            )
        if account_search:
            wiz_id = wizard.create({
                'jurnal_id': 8,
                'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
                'amount': account_search.amount_total,
                'payment_date': today,

            })
            wiz_id.action_create_payment()

        # Payment = self.env['account.payment'].with_context(default_invoice_ids=[(4, account_search.id, False)])
        
        # company = self.env.user.company_id.id
        # payment = Payment.create({
        #     # 'invoice_ids':[(6, 0,  account_search.ids, [])],
        #     'date': today,
        #     'payment_method_id': self.inbound_payment_method.id,
        #     'payment_type': 'inbound',
        #     'partner_type': 'customer',
        #     'partner_id': account_search.partner_id.id,
        #     'amount': 199000,
        #     'company_id': company.id,
        #     'reconciled_invoice_ids': [(6, 0,  account_search.ids, [])],
        # })
        # payment.post()

    def paid(self,*get):
        for i in get:
            self.write({
                'status_payment': "1"
                })
            self.unlock()
            if self.status_member == "1":
                self.add_month()
            if get.status_member == "2":
                self.add_year()
        return True
    
    
                    


from tempfile import mkstemp
from xendit import Xendit
from shutil import move
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta,date

class TempPartner(models.Model):
    _inherit = 'res.partner'
   
    exp_date = fields.Date(string='Expired Date')
    virtual_account = fields.Char(srting="Nomor VA")
    id_va = fields.Char(string="id")
    status_member = fields.Selection([
        ('1', '1 Bulan'),
        ('2','1 Tahun')
    ], string='status member')
    invoice_url=fields.Char(string="invoice_url")
    invoice_id=fields.Char(string="invoice_id")
    status_payment = fields.Selection([
        ('1', 'Paid'),
        ('0', 'Not Paid'),
    ], string='status payment')

    def add_month(self):
        if self.exp_date:
            for i in self:
                exp = i.exp_date + relativedelta(months=1)
                i.write({
                'exp_date': exp,
            })


    def add_year(self):
        if self.exp_date:
            for i in self:
                exp = i.exp_date + relativedelta(years=1)
                i.write({
                'exp_date': exp,
            })



    # @api.onchange('exp_date')
    def exp_db(self):
        today = date.today()
        exp_obj= self.env['res.partner'].search([('exp_date','=',today)])
        for exp in exp_obj:
            return {
        'type': 'ir.actions.act_url',
        'url': '/web/db_lock?db=%s' % exp.db,
        'target': 'self',
        'res_id': exp.id,
        }

    def unlock(self):
        for this in self:
            # if this.exp_date:
            #     today = datetime.now()
            #     if this.exp_date == today:
            return {
            'type': 'ir.actions.act_url',
            'url': '/web/db_unlock?db=%s' % self.db,
            'target': 'self',
            'res_id': this.id,
            }
    def generate_va(self):
        print(str(self.name),"test_print")
        
        api_key = "xnd_development_3uzESw7LPejhIz0UOsWh68eGRC3mjrbgiOHl1XCHWZUHi75eQ9nwu0zdcShw8A"
        xendit_instance = Xendit(api_key=api_key)
        VirtualAccount = xendit_instance.VirtualAccount
        va_name = self.name
        today = datetime.now()
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
        today=datetime.today()

        vals_line = []

        for this in self:
            if this.status_member == '1':
                if this.packet == '1':
                    product_obj = self.env['product.product'].search([('default_code','=','TR1')])
                    vals_line.append({
                        'product_id': product_obj.id,
                        'name': product_obj.name,
                        'price_unit':product_obj.lst_price
                    })
                elif this.packet == '2':
                    product_obj = self.env['product.product'].search([('default_code','=','CF1')])
                    vals_line.append({
                        'product_id': product_obj.id,
                        'name': product_obj.name,
                        'price_unit':product_obj.lst_price
                    })
                elif this.packet == '3':
                    product_obj = self.env['product.product'].search([('default_code','=','HO1')])
                    vals_line.append({
                        'product_id': product_obj.id,
                        'name': product_obj.name,
                        'price_unit':product_obj.lst_price
                    })
            if this.status_member == '2':
                if this.packet == '1':
                    product_obj = self.env['product.product'].search([('default_code','=','TR12')])
                    vals_line.append({
                        'product_id': product_obj.id,
                        'name': product_obj.name,
                        'price_unit':product_obj.lst_price
                    })
                elif this.packet == '2':
                    product_obj = self.env['product.product'].search([('default_code','=','CF12')])
                    vals_line.append({
                        'product_id': product_obj.id,
                        'name': product_obj.name,
                        'price_unit':product_obj.lst_price
                    })
                elif this.packet == '3':
                    product_obj = self.env['product.product'].search([('default_code','=','HO12')])
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
                'payment_reference':self.invoice_id,
                'invoice_line_ids':vals_line,
            })
        account_search = self.env['account.move'].search([('payment_reference','=',self.invoice_id)])
        account_search.action_post()


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
        ##packet toko retail
        if self.packet == "1":
            if self.status_member == '1':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=199000,
                    description="Invoice Retail Bulanan#"+str(self.name),
                    invoice_duration=259200,
                    customer = customer,
                    currency  = "IDR",  
                    payer_email =self.email,
                )
                dict_invoice = []
                dict_invoice.append(invoice)
            if self.status_member == '2':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=1990000,
                    description="Invoice Retail Tahunan#"+str(self.name),
                    invoice_duration=259200,
                    customer = customer,
                    currency  = "IDR",  
                    payer_email =self.email,
                )
                dict_invoice = []
                dict_invoice.append(invoice)

        ##packet Resto
        elif self.packet == "2":
            if self.status_member == '1':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=399000,
                    description="Invoice Retail Cafe & Resto Bulanan#"+str(self.name),
                    invoice_duration=259200,
                    customer = customer,
                    currency  = "IDR",  
                    payer_email =self.email,
                )
                dict_invoice = []
                dict_invoice.append(invoice)
            if self.status_member == '2':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=3990000,
                    description="Invoice Retail Cafe & Resto Tahunan#"+str(self.name),
                    invoice_duration=259200,
                    customer = customer,
                    currency  = "IDR",  
                    payer_email =self.email,
                )
                dict_invoice = []
                dict_invoice.append(invoice)

        ##packet Hotel
        elif self.packet == "3":
            if self.status_member == '1':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=599000,
                    description="Invoice Retail Hotel Bulanan#"+str(self.name),
                    currency  = "IDR",  
                    payer_email =self.email,
                )
                dict_invoice = []
                dict_invoice.append(invoice)
            if self.status_member == '1':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=5990000,
                    description="Invoice Retail Hotel Tahunan#"+str(self.name),
                    invoice_duration=259200,
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
            })

    def warning_payment(self):
        todays=date.today()
        has_exp = todays + timedelta(days=3)
        exp_obj= self.env['res.partner'].search([('exp_date','=',has_exp)])
        for this in exp_obj:
            print(exp_obj,'bisabisabi')
            
            this.create_xendit_invoice()
            this.get_invoice()
            this.create_invoice()
            
    def paid(self,*get):
            for i in get:
                self.write({
                    'status_payment': "1"
                    })
                self.unlock()
                if self.status_member == "1":
                   self.add_month()
                if self.status_member == "2":
                   self.add_year()
            print(self.status_payment,'testprint')
            return True


            

        
from tempfile import mkstemp
from xendit import Xendit
from shutil import move
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta,date

class TempPartner(models.Model):
    _inherit = 'res.partner'
   
    exp_date = fields.Date(string='Expired Date')
    virtual_account = fields.Char(srting="Nomor VA")
    id_va = fields.Char(string="id")
    status_member = fields.Selection([
        ('1', '1 Bulan'),
        ('2','1 Tahun')
    ], string='status member')
    invoice_url=fields.Char(string="invoice_url")
    invoice_id=fields.Char(string="invoice_id")
    status_payment = fields.Selection([
        ('1', 'Paid'),
        ('0', 'Not Paid'),
    ], string='status payment')

    def add_month(self):
        if self.exp_date:
            for i in self:
                exp = i.exp_date + relativedelta(months=1)
                i.write({
                'exp_date': exp,
            })


    def add_year(self):
        if self.exp_date:
            for i in self:
                exp = i.exp_date + relativedelta(years=1)
                i.write({
                'exp_date': exp,
            })



    # @api.onchange('exp_date')
    def exp_db(self):
        today = date.today()
        exp_obj= self.env['res.partner'].search([('exp_date','=',today)])
        for exp in exp_obj:
            return {
        'type': 'ir.actions.act_url',
        'url': '/web/db_lock?db=%s' % exp.db,
        'target': 'self',
        'res_id': exp.id,
        }

    def unlock(self):
        for this in self:
            # if this.exp_date:
            #     today = datetime.now()
            #     if this.exp_date == today:
            return {
            'type': 'ir.actions.act_url',
            'url': '/web/db_unlock?db=%s' % self.db,
            'target': 'self',
            'res_id': this.id,
            }
    def generate_va(self):
        print(str(self.name),"test_print")
        
        api_key = "xnd_development_3uzESw7LPejhIz0UOsWh68eGRC3mjrbgiOHl1XCHWZUHi75eQ9nwu0zdcShw8A"
        xendit_instance = Xendit(api_key=api_key)
        VirtualAccount = xendit_instance.VirtualAccount
        va_name = self.name
        today = datetime.now()
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
        today=datetime.today()

        vals_line = []

        for this in self:
            if this.status_member == '1':
                if this.packet == '1':
                    product_obj = self.env['product.product'].search([('default_code','=','TR1')])
                    vals_line.append({
                        'product_id': product_obj.id,
                        'name': product_obj.name,
                        'price_unit':product_obj.lst_price
                    })
                elif this.packet == '2':
                    product_obj = self.env['product.product'].search([('default_code','=','CF1')])
                    vals_line.append({
                        'product_id': product_obj.id,
                        'name': product_obj.name,
                        'price_unit':product_obj.lst_price
                    })
                elif this.packet == '3':
                    product_obj = self.env['product.product'].search([('default_code','=','HO1')])
                    vals_line.append({
                        'product_id': product_obj.id,
                        'name': product_obj.name,
                        'price_unit':product_obj.lst_price
                    })
            if this.status_member == '2':
                if this.packet == '1':
                    product_obj = self.env['product.product'].search([('default_code','=','TR12')])
                    vals_line.append({
                        'product_id': product_obj.id,
                        'name': product_obj.name,
                        'price_unit':product_obj.lst_price
                    })
                elif this.packet == '2':
                    product_obj = self.env['product.product'].search([('default_code','=','CF12')])
                    vals_line.append({
                        'product_id': product_obj.id,
                        'name': product_obj.name,
                        'price_unit':product_obj.lst_price
                    })
                elif this.packet == '3':
                    product_obj = self.env['product.product'].search([('default_code','=','HO12')])
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
                'payment_reference':self.invoice_id,
                'invoice_line_ids':vals_line,
            })
        account_search = self.env['account.move'].search([('payment_reference','=',self.invoice_id)])
        account_search.action_post()


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
        ##packet toko retail
        if self.packet == "1":
            if self.status_member == '1':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=199000,
                    description="Invoice Retail Bulanan#"+str(self.name),
                    invoice_duration=259200,
                    customer = customer,
                    currency  = "IDR",  
                    payer_email =self.email,
                )
                dict_invoice = []
                dict_invoice.append(invoice)
            if self.status_member == '2':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=1990000,
                    description="Invoice Retail Tahunan#"+str(self.name),
                    invoice_duration=259200,
                    customer = customer,
                    currency  = "IDR",  
                    payer_email =self.email,
                )
                dict_invoice = []
                dict_invoice.append(invoice)

        ##packet Resto
        elif self.packet == "2":
            if self.status_member == '1':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=399000,
                    description="Invoice Retail Cafe & Resto Bulanan#"+str(self.name),
                    invoice_duration=259200,
                    customer = customer,
                    currency  = "IDR",  
                    payer_email =self.email,
                )
                dict_invoice = []
                dict_invoice.append(invoice)
            if self.status_member == '2':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=3990000,
                    description="Invoice Retail Cafe & Resto Tahunan#"+str(self.name),
                    invoice_duration=259200,
                    customer = customer,
                    currency  = "IDR",  
                    payer_email =self.email,
                )
                dict_invoice = []
                dict_invoice.append(invoice)

        ##packet Hotel
        elif self.packet == "3":
            if self.status_member == '1':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=599000,
                    description="Invoice Retail Hotel Bulanan#"+str(self.name),
                    invoice_duration=259200,
                    customer = customer,
                    currency  = "IDR",  
                    payer_email =self.email,
                )
                dict_invoice = []
                dict_invoice.append(invoice)
            if self.status_member == '1':
                invoice = Invoice.create(
                    external_id="invoice"+str(ts),
                    amount=5990000,
                    description="Invoice Retail Hotel Tahunan#"+str(self.name),
                    invoice_duration=259200,
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
            })

    def warning_payment(self):
        todays=date.today()
        has_exp = todays + timedelta(days=3)
        exp_obj= self.env['res.partner'].search([('exp_date','=',has_exp)])
        for this in exp_obj:
            print(exp_obj,'bisabisabi')
            
            this.create_xendit_invoice()
            this.get_invoice()
            this.create_invoice()
            
    @api.onchange('status_payment')
    def regpaid(self):
        account_search = self.env['account.move'].search([('payment_reference','=',self.invoice_id)])
        today =datetime.now()
        if self.status_payment == "1":
            wizard = self.env['account.payment.register'].with_context(
                    active_model = 'account.move',
                    active_ids = account_search.ids,
                )
            wiz_id = wizard.create({
                'jurnal_id': 8,
                'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
                'amount': account_search.amount_total,
                'payment_date': today,

            })
            wiz_id.action_create_payment()
            
    def paid(self,*get):
            for i in get:
                self.write({
                    'status_payment': "1"
                    })


                self.unlock()
                if self.status_member == "1":
                   self.add_month()
                if self.status_member == "2":
                   self.add_year()
            print(self.status_payment,'testprint')            
            return True


            

        