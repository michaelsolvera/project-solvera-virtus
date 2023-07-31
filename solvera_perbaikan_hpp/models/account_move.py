
from datetime import datetime,timedelta
from shutil import move
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero

class stockmove(models.Model):
    _inherit = 'stock.move'
    no_update = fields.Boolean(string='no update',default=False)
class stockmove(models.Model):
    _inherit = 'stock.picking'


    def perbaikanvs(self):
        string_input_with_date = "2023/03/01"
        past = datetime.strptime(string_input_with_date, "%Y/%m/%d")
        picking_obj = self.env['stock.picking'].search([('picking_type_code','=',"internal")],order='product_id,id asc')

        for i in picking_obj :
            if i.date > past:
                for line in i.move_lines:
                    valuation_obj = self.env['stock.valuation.layer'].search([('stock_move_id','=',line.id)],order='product_id,id asc,value desc')
                    temp=0
                    for val in valuation_obj:
                        # accout_obj = self.env['account.move'].search([('stock_move_id','=',line.id)])
                        # for acc in accout_obj:
                        if temp==0:
                            temp=abs(val.value)
                        else:
                            val.sudo().write({
                            'unit_cost': abs(temp/val.quantity),
                            'value':abs(temp)
                            })
                            temp=0
                            
                    #     print(val.value,i.name,val.description,'print valu sehrausnya',temp)
                    # print("end")
                        # if temp == 0:
                        #     temp=val.value
                        # else:
                        #     if abs(temp) != val.value:
                                # val.sudo().write({
                                # 'unit_cost': abs(temp/val.quantity),
                                # 'value':abs(temp)
                                # })
    def perbaikanje(self):
        string_input_with_date = "2023/03/01"
        past = datetime.strptime(string_input_with_date, "%Y/%m/%d")
        picking_obj = self.env['stock.picking'].search([('picking_type_code','=',"internal")],order='product_id,id asc')

        for i in picking_obj :
            if i.date > past:
                if i.id != 4345:
                    for line in i.move_lines:
                        accout_obj = self.env['account.move'].search([('stock_move_id','=',line.id),('state','=','posted')])               
                        temp=0
                        for val in accout_obj:
                            valuation_obj = self.env['stock.valuation.layer'].search([('stock_move_id','=',val.stock_move_id.id)],order='product_id,id asc,value desc')
                            for valuation in valuation_obj:
                                if valuation.stock_move_id.id == val.stock_move_id.id:
                                    for lines in val.line_ids:
                                    #     if lines.debit:
                                    #         print(val.name,i.name,valuation.value,lines.debit,'debit',temp)
                                    #     if lines.credit:
                                    #         print(val.name,i.name,valuation.value,lines.credit,'credit',temp)
                                        if lines.debit:
                                            lines.with_context(check_move_validity=False).write({
                                                'debit': abs(valuation.value),
                                            })
                                        if lines.credit:
                                            lines.with_context(check_move_validity=False).write({
                                                'credit': abs(valuation.value),
                                            })
                        # print("end")
                            # if temp == 0:
                            #     temp=val.value
                            # else:
                            #     if abs(temp) != val.value:
                                    # val.sudo().write({
                                    # 'unit_cost': abs(temp/val.quantity),
                                    # 'value':abs(temp)
                                    # })
                                        
                    


class accountmove(models.Model):
    _inherit = 'stock.valuation.layer'

    def cek_picking(self):
        # picking_obj = self.env['stock.move'].search([('id','=',"13208")])
        picking_obj = self.env['stock.picking'].search([('id','=',"3826")])
        move_obj=self.env['account.move']
        for line in picking_obj.move_ids_without_package:
            move_lines = [
                        (0, 0, {
                            'account_id':line.product_id.categ_id.property_stock_valuation_account_id.id,
                            'name': str(picking_obj.name)+' - '+line.product_id.name,
                            'credit':line.product_id.standard_price_jakarta*line.quantity_done*1,
                            'currency_id':picking_obj.company_id.currency_id.id,
                        }),
                        (0, 0, {
                            'account_id':line.product_id.categ_id.property_stock_account_output_categ_id.id,
                            'name': str(picking_obj.name)+' - '+line.product_id.name,
                            'debit':line.product_id.standard_price_jakarta*line.quantity_done*1,
                            'currency_id':picking_obj.company_id.currency_id.id,
                        }),
                        ]
            
            move_id = move_obj.sudo().create({
                'ref':str(picking_obj._origin.name)+' - '+line.product_id.name,
                'date':line.create_date,
                'journal_id':6,
                'line_ids': move_lines,
                'branch_id':line.location_dest_id.branch_id.id,
                'stock_move_id':13208
            })
            move_id.sudo().post()
        
            valuation_obj = self.env['stock.valuation.layer']
            valuation_obj.sudo().create({
                                'create_date':line.create_date,
                                'product_id': line.product_id.id,
                                'quantity': line.quantity_done*1,
                                'uom_id':line.product_uom.id,
                                'unit_cost':line.product_id.standard_price_jakarta,
                                'value':line.product_id.standard_price_jakarta*line.quantity_done*-1,
                                'description':str(picking_obj.name)+' - '+line.product_id.name,
                                'company_id': line.company_id.id,
                                'stock_move_id':13208,
                                'branch_id': line.location_dest_id.branch_id.id,
                                'account_move_id':move_id.id,
                            })

       

    def manufacture_price_14nov(self):
        mrp_obj = self.env['mrp.production'].search([],order='product_id,id asc')
        temp=0
        for i in mrp_obj:
            string_input_with_date = "2023/04/01"
            past = datetime.strptime(string_input_with_date, "%Y/%m/%d")
            if i.create_date > past:

                for line in i.move_raw_ids:
                    svl_obj=self.env['stock.valuation.layer'].search([('stock_move_id','=',line.id)])
                    for lines in svl_obj:
                        temp=temp+lines.value
                        
                for linef in i.move_finished_ids:
                    svl_obj_f=self.env['stock.valuation.layer'].search([('stock_move_id','=',linef.id)])
                    for linesf in svl_obj_f:
                        linesf.sudo().write({
                        'unit_cost': abs(temp/linesf.quantity),
                        'value':abs(temp)
                        })
                        journal_obj = self.env['account.move'].search([('id','=',linesf.account_move_id.id)])
                        for line in journal_obj.line_ids:
                            if line.debit:
                                line.with_context(check_move_validity=False).write({
                                    'debit': abs(temp),
                                })
                            if line.credit:
                                line.with_context(check_move_validity=False).write({
                                    'credit': abs(temp),
                                })
                        temp=0

    def cek_update_okt(self):
        valuation_obj = self.env['stock.valuation.layer'].search([],order='product_id,id asc')
        for i in valuation_obj:
            string_input_with_date = "2022/05/01"
            past = datetime.strptime(string_input_with_date, "%Y/%m/%d")
            if i.create_date < past:
                # print(i.stock_move_id.no_update,'cek_tanggalPrint')
                i.stock_move_id.no_update=True  
    
    def update_reference(self):
        move_obj = self.env['stock.move'].search([])

        for i in move_obj:
            # for val in i.stock_valuation_layer_ids:
            #     print(val.value)
            for line in i.account_move_ids:
                line.write({
                    'ref' : i.reference+" - "+i.product_id.name
                })
                for lines in line.line_ids:
                    lines.write({
                        'name': i.reference+" - "+i.product_id.name
                    })
    def update_reference_value(self):
        move_obj = self.env['stock.move'].search([])

        for i in move_obj:
            for val in i.stock_valuation_layer_ids:
                for line in i.account_move_ids:
                    if val.description == line.ref:
                        for lines in line.line_ids:
                            if lines.debit:
                                lines.with_context(check_move_validity=False).write({
                                    'debit':abs(val.value),
                                })
                            if lines.credit:
                                lines.with_context(check_move_validity=False).write({
                                    'credit':abs(val.value),
                                })
    def update_initial_6970(self):
        valuation_obj = self.env['stock.valuation.layer'].search([('id','=',6970)],order='product_id,stock_move_id asc,value asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            i.sudo().write({
            'unit_cost': 140.66,
            'value': 2109861.75,
            })
            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
            for line in journal_obj.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                        'debit': 2109861.75,
                    })
                if line.credit:
                    line.with_context(check_move_validity=False).write({
                        'credit':2109861.75,
                    })

                    1251.20
    def update_initial_2629(self):
        valuation_obj = self.env['stock.valuation.layer'].search([('id','=',2629)],order='product_id,stock_move_id asc,value asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            i.sudo().write({
            'unit_cost': 1251.20,
            'value': 250240.00,
            })
            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
            for line in journal_obj.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                        'debit': 250240.00,
                    })
                if line.credit:
                    line.with_context(check_move_validity=False).write({
                        'credit':250240.00,
                    })

    def update_initial_23584(self):
        valuation_obj = self.env['stock.valuation.layer'].search([('id','=',23584)],order='product_id,stock_move_id asc,value asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            i.sudo().write({
            'unit_cost': 870.26,
            'value': 3916170,
            })
            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
            for line in journal_obj.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                        'debit': 3916170,
                    })
                if line.credit:
                    line.with_context(check_move_validity=False).write({
                        'credit':3916170,
                    })
    def update_initial_22000(self):
        valuation_obj = self.env['stock.valuation.layer'].search([('id','=',22000)],order='product_id,stock_move_id asc,value asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            i.sudo().write({
            'unit_cost': 1791.33,
            'value': 1073006.67,
            })
            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
            for line in journal_obj.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                        'debit': 1073006.67,
                    })
                if line.credit:
                    line.with_context(check_move_validity=False).write({
                        'credit':1073006.67,
                    })
    def update_initial_25322(self):
        valuation_obj = self.env['stock.valuation.layer'].search([('id','=',25322)],order='product_id,stock_move_id asc,value asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            i.sudo().write({
            'unit_cost': 1791.33,
            'value': 1074798,
            })
            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
            for line in journal_obj.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                        'debit': 1074798,
                    })
                if line.credit:
                    line.with_context(check_move_validity=False).write({
                        'credit':1074798,
                    })
    def update_initial_22088(self):
        valuation_obj = self.env['stock.valuation.layer'].search([('id','=',22088)],order='product_id,stock_move_id asc,value asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            i.sudo().write({
            'unit_cost': 1791.33,
            'value': -1074798,
            })
            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
            for line in journal_obj.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                        'debit': 1074798,
                    })
                if line.credit:
                    line.with_context(check_move_validity=False).write({
                        'credit':1074798,
                    })

    def update_initial_22089(self):
        valuation_obj = self.env['stock.valuation.layer'].search([('id','=',22089)],order='product_id,stock_move_id asc,value asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            i.sudo().write({
            'unit_cost': 1791.33,
            'value': 1074798,
            })
            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
            for line in journal_obj.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                        'debit': 1074798,
                    })
                if line.credit:
                    line.with_context(check_move_validity=False).write({
                        'credit':1074798,
                    })
    def update_initial_21999(self):
        valuation_obj = self.env['stock.valuation.layer'].search([('id','=',21999)],order='product_id,stock_move_id asc,value asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            i.sudo().write({
            'unit_cost': 1791.33,
            'value': 1791.33,
            })
            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
            for line in journal_obj.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                        'debit':1791.33,
                    })
                if line.credit:
                    line.with_context(check_move_validity=False).write({
                        'credit':1791.33,
                    })


    def update_initial_1630(self):
        valuation_obj = self.env['stock.valuation.layer'].search([('id','=',1630)],order='product_id,stock_move_id asc,value asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            i.sudo().write({
            'unit_cost': 141.55,
            'value': -849300.00,
            'quantity': -6000
            })
            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
            for line in journal_obj.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                        'debit': 849300.00,
                    })
                if line.credit:
                    line.with_context(check_move_validity=False).write({
                        'credit': 849300.00,
                    })
    def update_initial_7012(self):
        valuation_obj = self.env['stock.valuation.layer'].search([('id','=',7012)],order='product_id,stock_move_id asc,value asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            i.sudo().write({
            'unit_cost': 253.54,
            'value': 912726.05,
            })
            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
            for line in journal_obj.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                        'debit': 912726.05,
                    })
                if line.credit:
                    line.with_context(check_move_validity=False).write({
                        'credit': 912726.05,
                    })

    def update_initial_2204(self):
        valuation_obj = self.env['stock.valuation.layer'].search([('id','=',2204)],order='product_id,stock_move_id asc,value asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            i.sudo().write({
            'unit_cost': 597.5102268,
            'value': -2151022.68
            })
            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
            for line in journal_obj.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                        'debit': 2151022.68,
                    })
                if line.credit:
                    line.with_context(check_move_validity=False).write({
                        'credit': 2151022.68,
                    })
    def update_initial_4068(self):
        valuation_obj = self.env['stock.valuation.layer'].search([('id','=',4068)],order='product_id,stock_move_id asc,value asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            i.sudo().write({
            'unit_cost':432.38,
            'value': 518852.37,
            })
            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
            for line in journal_obj.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                        'debit': 518852.37,
                    })
                if line.credit:
                    line.with_context(check_move_validity=False).write({
                        'credit': 518852.37,
                    })
    def update_initial_4068(self):
        valuation_obj = self.env['stock.valuation.layer'].search([('id','=',4068)],order='product_id,stock_move_id asc,value asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            i.sudo().write({
            'unit_cost':432.38,
            'value': 518852.37,
            })
            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
            for line in journal_obj.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                        'debit': 518852.37,
                    })
                if line.credit:
                    line.with_context(check_move_validity=False).write({
                        'credit': 518852.37,
                    })
    def update_initial_4067(self):
        valuation_obj = self.env['stock.valuation.layer'].search([('id','=',4067)],order='product_id,stock_move_id asc,value asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            i.sudo().write({
            'unit_cost':432.38,
            'value': -518852.37,
            })
            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
            for line in journal_obj.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                        'debit': 518852.37,
                    })
                if line.credit:
                    line.with_context(check_move_validity=False).write({
                        'credit': 518852.37,
                    })
    def update_initial_7978(self):
            valuation_obj = self.env['stock.valuation.layer'].search([('id','=',7978)],order='product_id,stock_move_id asc,value asc')
            product=[]
            cost = 0
            temp=0
            value=0
            for i in valuation_obj:
                i.sudo().write({
                'unit_cost':840.71,
                'value': -504426,
                })
                journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                for line in journal_obj.line_ids:
                    if line.debit:
                        line.with_context(check_move_validity=False).write({
                            'debit': 504426,
                        })
                    if line.credit:
                        line.with_context(check_move_validity=False).write({
                            'credit': 504426,
                        })
    def update_initial_7979(self):
        valuation_obj = self.env['stock.valuation.layer'].search([('id','=',7979)],order='product_id,stock_move_id asc,value asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            i.sudo().write({
            'unit_cost':840.71,
            'value': 504426,
            })
            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
            for line in journal_obj.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                        'debit': 504426,
                    })
                if line.credit:
                    line.with_context(check_move_validity=False).write({
                        'credit': 504426,
                    })
    def update_initial_7979(self):
        valuation_obj = self.env['stock.valuation.layer'].search([('id','=',7979)],order='product_id,stock_move_id asc,value asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            i.sudo().write({
            'unit_cost':840.71,
            'value': 504426,
            })
            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
            for line in journal_obj.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                        'debit': 504426,
                    })
                if line.credit:
                    line.with_context(check_move_validity=False).write({
                        'credit': 504426,
                    })
    def update_initial_8946(self):
        valuation_obj = self.env['stock.valuation.layer'].search([('id','=',8946)],order='product_id,stock_move_id asc,value asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            i.sudo().write({
            'unit_cost':1487.36,
            'value': 14873600,
            })
            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
            for line in journal_obj.line_ids:
                if line.debit:
                    line.with_context(check_move_validity=False).write({
                        'debit': 14873600,
                    })
                if line.credit:
                    line.with_context(check_move_validity=False).write({
                        'credit': 14873600,
                    })



                    


    def cek(self):
        valuation_obj = self.env['stock.valuation.layer'].search([],order='product_id,stock_move_id asc,value asc')
        # picking_obj = self.env['stock.picking.layer'].search([],order='product_id,id asc')
        move_id = False
        cost=0
        value=0
        for i in valuation_obj:
            if i.stock_move_id.picking_code == 'internal':
                if i.stock_move_id.reference != "WHJ/INTJS/00012":
                
                    if i.stock_move_id.id != move_id:
                        move_id= i.stock_move_id.id
                        value=abs(i.value)
                    else:
                        if i.branch_id != i.stock_move_id.location_id: 
                            if value != 0 and i.quantity != 0:
                                if i.quantity > 0:
                                    cost=abs(value/i.quantity)
                                    print(i.product_id.name,'test_vlue',i.value,'test_val_replace',i.value,cost)
                                    i.sudo().write({
                                    'unit_cost': abs(value/i.quantity),
                                    'value':abs(value)
                                    })
                                    journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                                    for line in journal_obj.line_ids:
                                        if line.debit:
                                            line.with_context(check_move_validity=False).write({
                                                'debit': abs(value),
                                            })
                                        if line.credit:
                                            line.with_context(check_move_validity=False).write({
                                                'credit': abs(value),
                                            })
                                else:
                                    print(i.product_id.name,'test_vlue_minus',i.value,'test_val_replace',i.value,cost)
                                    i.sudo().write({
                                    'unit_cost': abs(value/i.quantity),
                                    'value':abs(value)*-1
                                    })
                                    journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                                    for line in journal_obj.line_ids:
                                        if line.debit:
                                            line.with_context(check_move_validity=False).write({
                                                'debit': abs(value),
                                            })
                                        if line.credit:
                                            line.with_context(check_move_validity=False).write({
                                                'credit': abs(value),
                                            })

                            print(i.product_id.name,'test_vlue2',i.value,'test_val_replace2',i.value)
                        else:
                            print(i.product_id.name,'test_vlue2',i.value,'test_val_replace2',i.value)    
    def cek_update0(self):
        valuation_obj = self.env['stock.valuation.layer'].search([],order='product_id,id asc')
        for i in valuation_obj:
            i.stock_move_id.no_update=False  

    def cek_update1(self):
        valuation_obj = self.env['stock.valuation.layer'].search([],order='product_id,id asc')
        for i in valuation_obj:
            if i.stock_move_id.location_id.id ==4:
                i.stock_move_id.no_update=True  
 
    def cek_update2(self):
        valuation_obj = self.env['stock.valuation.layer'].search([],order='product_id,id asc')
        for i in valuation_obj:
            if i.stock_move_id.picking_code == 'internal':
                i.stock_move_id.no_update=True

    


    def manufacture_ident2(self):
        mrp_obj = self.env['mrp.production'].search([],order='product_id,id asc')

        for i in mrp_obj:
            for line in i.move_raw_ids:
                svl_obj=self.env['stock.valuation.layer'].search([('stock_move_id','=',line.id)])
                for lines in svl_obj:
                    lines.stock_move_id.no_update=True
            for linef in i.move_finished_ids:
                svl_obj_f=self.env['stock.valuation.layer'].search([('stock_move_id','=',linef.id)])
                for linesf in svl_obj_f:
                    linesf.stock_move_id.no_update=True
    def manufacture_price(self):
        mrp_obj = self.env['mrp.production'].search([],order='product_id,id asc')
        temp=0
        for i in mrp_obj:
            if i.id != 28:
                for line in i.move_raw_ids:
                    svl_obj=self.env['stock.valuation.layer'].search([('stock_move_id','=',line.id)])
                    for lines in svl_obj:
                        temp=temp+lines.value
                        
                for linef in i.move_finished_ids:
                    svl_obj_f=self.env['stock.valuation.layer'].search([('stock_move_id','=',linef.id)])
                    for linesf in svl_obj_f:
                        linesf.sudo().write({
                        'unit_cost': abs(temp/linesf.quantity),
                        'value':abs(temp)
                        })
                        journal_obj = self.env['account.move'].search([('id','=',linesf.account_move_id.id)])
                        for line in journal_obj.line_ids:
                            if line.debit:
                                line.with_context(check_move_validity=False).write({
                                    'debit': abs(temp),
                                })
                            if line.credit:
                                line.with_context(check_move_validity=False).write({
                                    'credit': abs(temp),
                                })
                        temp=0
    def manufacture_ident(self):
        mrp_obj = self.env['mrp.production'].search([],order='product_id,id asc')

        for i in mrp_obj:
            for line in i.move_raw_ids:
                svl_obj=self.env['stock.valuation.layer'].search([('stock_move_id','=',line.id)])
                for lines in svl_obj:
                    lines.stock_move_id.no_update=False
            for linef in i.move_finished_ids:
                svl_obj_f=self.env['stock.valuation.layer'].search([('stock_move_id','=',linef.id)])
                for linesf in svl_obj_f:
                    linesf.stock_move_id.no_update=True


    def perbaikan_hpp_super_kai_jakarta(self):
        string_input_with_date = "2022/05/01"
        past = datetime.strptime(string_input_with_date, "%Y/%m/%d")
        valuation_obj = self.env['stock.valuation.layer'].search([('create_date','>',past)],order='product_id,id asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            if i.branch_id.id == 1:
                if i.product_id != product:
                    product=i.product_id
                    cost = round(i.value/i.quantity,7)
                    quantity = round(i.quantity,7)
                    temp=round(i.value/i.quantity,7)
                    
                else:
                    cost = round(cost,7)
                    cost_temp = round(cost,7)
                    quantity = round(quantity +i.quantity,7)
                    temp = round(i.unit_cost,7)
                    value = i.value
                    i.sudo().write({
                    'unit_cost': cost,
                    'value':round(cost,7)*i.quantity
                    })
                    journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                    for line in journal_obj.line_ids:
                        if line.debit:
                            line.with_context(check_move_validity=False).write({
                                'debit': abs(round(cost,7)*i.quantity),
                            })
                        if line.credit:
                            line.with_context(check_move_validity=False).write({
                                'credit': abs(round(cost,7)*i.quantity),
                            })
                    if i.stock_move_id.no_update == True:
                        if  i.quantity > 0 :
                            quant=quantity+i.quantity
                            if quantity != 0:
                                cost = ((round(cost_temp,7)*(quantity-i.quantity))+(round(temp,7)*i.quantity))/quantity
                            else:
                                cost= round(cost,7)
                            value = value
                        else:
                            cost = round(cost,7)
                            value = i.value
                        if i.quantity != 0:
                            i.sudo().write({
                            'unit_cost': value/i.quantity,
                            'value':value
                            })
                            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                            for line in journal_obj.line_ids:
                                if line.debit:
                                    line.with_context(check_move_validity=False).write({
                                        'debit': abs(value),
                                    })
                                if line.credit:
                                    line.with_context(check_move_validity=False).write({
                                        'credit': abs(value),
                                    })
                        else:
                            i.sudo().write({
                            'unit_cost': i.unit_cost,
                            'value':value
                            })
                            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                            for line in journal_obj.line_ids:
                                if line.debit:
                                    line.with_context(check_move_validity=False).write({
                                        'debit': abs(value),
                                    })
                                if line.credit:
                                    line.with_context(check_move_validity=False).write({
                                        'credit': abs(value),
                                    })

                    cost_temp = i.unit_cost
                        


    def perbaikan_hpp_super_kai_surabaya(self):
        string_input_with_date = "2022/05/01"
        past = datetime.strptime(string_input_with_date, "%Y/%m/%d")
        valuation_obj = self.env['stock.valuation.layer'].search([('create_date','>',past)],order='product_id,id asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            if i.branch_id.id == 2:
                if i.product_id != product:
                    product=i.product_id
                    cost = round(i.value/i.quantity,7)
                    quantity = round(i.quantity,7)
                    temp=round(i.value/i.quantity,7)
                    
                else:
                    cost = round(cost,7)
                    cost_temp = round(cost,7)
                    quantity = round(quantity +i.quantity,7)

                    temp = round(i.unit_cost,7)
                    value = i.value
                    print(cost,'test',temp,'pr',i.product_id.name,value)
                    i.sudo().write({
                    'unit_cost': cost,
                    'value':round(cost,7)*i.quantity
                    })
                    journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                    for line in journal_obj.line_ids:
                        if line.debit:
                            line.with_context(check_move_validity=False).write({
                                'debit': abs(round(cost,7)*i.quantity),
                            })
                        if line.credit:
                            line.with_context(check_move_validity=False).write({
                                'credit': abs(round(cost,7)*i.quantity),
                            })
                    if i.stock_move_id.no_update == True:
                        if  i.quantity > 0 :
                            quant=quantity+i.quantity
                            if quantity != 0:
                                cost = ((round(cost_temp,7)*(quantity-i.quantity))+(round(temp,7)*i.quantity))/quantity
                            else:
                                cost= round(cost,7)
                            value = value
                        else:
                            cost = round(cost,7)
                            value = i.value
                        if i.quantity != 0:
                            i.sudo().write({
                            'unit_cost': value/i.quantity,
                            'value':value
                            })
                            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                            for line in journal_obj.line_ids:
                                if line.debit:
                                    line.with_context(check_move_validity=False).write({
                                        'debit': abs(value),
                                    })
                                if line.credit:
                                    line.with_context(check_move_validity=False).write({
                                        'credit': abs(value),
                                    })
                        else:
                            i.sudo().write({
                            'unit_cost': i.unit_cost,
                            'value':value
                            })
                            journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                            for line in journal_obj.line_ids:
                                if line.debit:
                                    line.with_context(check_move_validity=False).write({
                                        'debit': abs(value),
                                    })
                                if line.credit:
                                    line.with_context(check_move_validity=False).write({
                                        'credit': abs(value),
                                    })

                    cost_temp = i.unit_cost


    def perbaikan_hpp_super_kai_bali(self):
        string_input_with_date = "2022/05/01"
        past = datetime.strptime(string_input_with_date, "%Y/%m/%d")
        valuation_obj = self.env['stock.valuation.layer'].search([('create_date','>',past)],order='product_id,id asc')
        product=[]
        cost = 0
        temp=0
        value=0
        for i in valuation_obj:
            if i.value !=0:
                if i.branch_id.id == 3:
                    if i.product_id != product:
                        product=i.product_id
                        cost = round(i.value/i.quantity,7)
                        quantity = round(i.quantity,7)
                        print(quantity,i.product_id.name)
                        temp=round(i.value/i.quantity,7)
                        
                    else:
                        cost = round(cost,7)
                        cost_temp = round(cost,7)
                        quantity = round(quantity +i.quantity,7)
                        temp = round(i.unit_cost,7)
                        value = i.value
                        i.sudo().write({
                        'unit_cost': cost,
                        'value':round(cost,7)*i.quantity
                        })
                        journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                        for line in journal_obj.line_ids:
                            if line.debit:
                                line.with_context(check_move_validity=False).write({
                                    'debit': abs(round(cost,7)*i.quantity),
                                })
                            if line.credit:
                                line.with_context(check_move_validity=False).write({
                                    'credit': abs(round(cost,7)*i.quantity),
                                })
                        if i.stock_move_id.no_update == True:
                            if  i.quantity > 0 :
                                quant=quantity+i.quantity
                                if quantity != 0:
                                    cost = ((round(cost_temp,7)*(quantity-i.quantity))+(round(temp,7)*i.quantity))/quantity
                                else:
                                    cost= round(cost,7)
                                value = value

                            else:
                                cost = round(cost,7)
                                value = i.value
                            if i.quantity != 0:

                                i.sudo().write({
                                'unit_cost': value/i.quantity,
                                'value':value
                                })
                                journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                                for line in journal_obj.line_ids:
                                    if line.debit:
                                        line.with_context(check_move_validity=False).write({
                                            'debit': abs(value),
                                        })
                                    if line.credit:
                                        line.with_context(check_move_validity=False).write({
                                            'credit': abs(value),
                                        })
                            else:
                                i.sudo().write({
                                'unit_cost': i.unit_cost,
                                'value':value
                                })
                                journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                                for line in journal_obj.line_ids:
                                    if line.debit:
                                        line.with_context(check_move_validity=False).write({
                                            'debit': abs(value),
                                        })
                                    if line.credit:
                                        line.with_context(check_move_validity=False).write({
                                            'credit': abs(value),
                                        })

                        cost_temp = i.unit_cost
     
    def perbaikan_hpp_super_kai_jakarta2(self):
        valuation_obj = self.env['stock.valuation.layer'].search([],order='product_id,id asc')
        product=[]
        cost = 0
        temp=0
        for i in valuation_obj:
            if i.branch_id.id == 1:
                if i.product_id != product:
                    product=i.product_id
                    cost = i.value/i.quantity
                    quantity = i.quantity
                    temp=i.unit_cost
                   
                else:
                    cost = round(cost,7)
                    quantity = quantity +i.quantity
                    temp = round(temp,7)
                    if i.stock_move_id.picking_code != 'internal' or i.stock_move_id.location_id.id !=4:
                        i.sudo().write({
                        'unit_cost': cost,
                        'value':cost*i.quantity
                        })
                        journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                        for line in journal_obj.line_ids:
                            if line.debit:
                                line.with_context(check_move_validity=False).write({
                                    'debit': abs(round(cost,7)*i.quantity),
                                })
                            if line.credit:
                                line.with_context(check_move_validity=False).write({
                                    'credit': abs(round(cost,7)*i.quantity),
                                })
                    if i.stock_move_id.picking_code == 'internal' or i.stock_move_id.location_id.id ==4:
                        if  i.quantity > 0 :
                            quant=quantity+i.quantity
                            if quant != 0:
                                cost = ((round(cost,7)*quantity)+(round(temp,7)*i.quantity))/quant
                            else:
                                cost= round(temp,7)
                        else:
                            cost = round(temp,7)
                        


    def perbaikan_hpp_super_kai_surabaya2(self):
        valuation_obj = self.env['stock.valuation.layer'].search([],order='product_id,id asc')
        product=[]
        cost = 0
        temp=0
        for i in valuation_obj:
            if i.branch_id.id == 2:
                if i.product_id != product:
                    product=i.product_id
                    cost = i.value/i.quantity
                    quantity = i.quantity
                    temp=i.unit_cost
                   
                else:
                    cost = round(cost,7)
                    quantity = quantity +i.quantity
                    temp = round(temp,7)
                    if i.stock_move_id.picking_code != 'internal' or i.stock_move_id.location_id.id !=4:
                        i.sudo().write({
                        'unit_cost': cost,
                        'value':cost*i.quantity
                        })
                        journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                        for line in journal_obj.line_ids:
                            if line.debit:
                                line.with_context(check_move_validity=False).write({
                                    'debit': abs(round(cost,7)*i.quantity),
                                })
                            if line.credit:
                                line.with_context(check_move_validity=False).write({
                                    'credit': abs(round(cost,7)*i.quantity),
                                })
                    if i.stock_move_id.picking_code == 'internal' or i.stock_move_id.location_id.id ==4:
                        if  i.quantity > 0 :
                            quant=quantity+i.quantity
                            if quant != 0:
                                cost = ((round(cost,7)*quantity)+(round(temp,7)*i.quantity))/quant
                            else:
                                cost= round(temp,7)
                        else:
                            cost = round(temp,7)
                                 


    def perbaikan_hpp_super_kai_bali2(self):
        
        string_input_with_date = "2023/05/01"
        past = datetime.strptime(string_input_with_date, "%Y/%m/%d")
        valuation_obj = self.env['stock.valuation.layer'].search([('create_date','>',past)],order='product_id,id asc')
        product=[]
        cost = 0
        temp=0
        for i in valuation_obj:
            if i.branch_id.id == 3:
                if i.product_id != product:
                    product=i.product_id
                    cost = i.value/i.quantity
                    quantity = i.quantity
                    temp=i.unit_cost
                   
                else:
                    cost = round(cost,7)
                    quantity = quantity +i.quantity
                    temp = round(temp,7)
                    if i.stock_move_id.picking_code != 'internal' or i.stock_move_id.location_id.id !=4:
                        i.sudo().write({
                        'unit_cost': cost,
                        'value':cost*i.quantity
                        })
                        journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                        for line in journal_obj.line_ids:
                            if line.debit:
                                line.with_context(check_move_validity=False).write({
                                    'debit': abs(round(cost,7)*i.quantity),
                                })
                            if line.credit:
                                line.with_context(check_move_validity=False).write({
                                    'credit': abs(round(cost,7)*i.quantity),
                                })
                    if i.stock_move_id.picking_code == 'internal' or i.stock_move_id.location_id.id ==4:
                        if  i.quantity > 0 :
                            quant=quantity+i.quantity
                            if quant != 0:
                                cost = ((round(cost,7)*quantity)+(round(temp,7)*i.quantity))/quant
                            else:
                                cost= round(temp,7)
                        else:
                            cost = round(temp,7)
                      

   
        


    # def perbaikan_hpp_kai_jakarta(self):
    #     valuation_obj = self.env['stock.valuation.layer'].search([],order='product_id,id desc')
    #     value=0
    #     avco =0
    #     product=None
    #     for i in valuation_obj:
    #         if i.branch_id.id == 1 and i.value != 0:
    #             if product == i.product_id:
    #                 cost=temp
    #                 product=i.product_id
    #                 value=value+i.value
    #                 quantity = i.quantity+quantity

    #                 if quantity != 0:
    #                     avco=abs(value/quantity)
    #                 elif quantity == 0:
    #                     avco=abs(i.value /i.quantity)
    #             else:
                    
    #                 product=i.product_id
    #                 value=i.value
    #                 quantity=i.quantity
    #                 avco = abs(i.product_id.standard_price_jakarta)

    #             i.sudo().write({
    #                 'unit_cost': avco,
    #             })
    #             journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
    #             for line in journal_obj.line_ids:
    #                 if line.debit:
    #                     line.with_context(check_move_validity=False).write({
    #                         'debit': abs(avco*i.quantity),
    #                     })
    #                 if line.credit:
    #                     line.with_context(check_move_validity=False).write({
    #                         'credit': abs(avco*i.quantity),
    #                     })
    # def perbaikan_hpp_kai_surabaya(self):
    #     valuation_obj = self.env['stock.valuation.layer'].search([],order='product_id,id desc')
    #     value=0
    #     avco =0
    #     product=None
    #     for i in valuation_obj:
    #         if i.branch_id.id == 2 and i.value != 0:
    #             if product == i.product_id:
    #                 cost=temp
    #                 product=i.product_id
    #                 value=value+i.value
    #                 quantity = i.quantity+quantity

    #                 if quantity != 0:
    #                     avco=abs(value/quantity)
    #                 elif quantity == 0:
    #                     avco=abs(i.value /i.quantity)
  
                
    #             else:
                    
    #                 product=i.product_id
    #                 value=i.value
    #                 quantity=i.quantity
    #                 avco = abs(i.product_id.standard_price_surabaya)

    #             i.sudo().write({
    #                 'unit_cost': avco,
    #             })
    #             journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
    #             for line in journal_obj.line_ids:
    #                 if line.debit:
    #                     line.with_context(check_move_validity=False).write({
    #                         'debit': abs(avco*i.quantity),
    #                     })
    #                 if line.credit:
    #                     line.with_context(check_move_validity=False).write({
    #                         'credit': abs(avco*i.quantity),
    #                     })
    # def perbaikan_hpp_kai_bali(self):
    #     valuation_obj = self.env['stock.valuation.layer'].search([],order='product_id,id desc')
    #     value=0
    #     avco =0
    #     product=None
    #     for i in valuation_obj:
    #         if i.branch_id.id == 3 and i.value != 0:
    #             if product == i.product_id:
    #                 cost=temp
    #                 product=i.product_id
    #                 value=value+i.value
    #                 quantity = i.quantity+quantity

    #                 if quantity != 0:
    #                     avco=abs(value/quantity)
    #                 elif quantity == 0:
    #                     avco=abs(i.value /i.quantity)
  
                
    #             else:
                    
    #                 product=i.product_id
    #                 value=i.value
    #                 quantity=i.quantity
    #                 avco = abs(i.product_id.standard_price_bali)

    #             i.sudo().write({
    #                 'unit_cost': avco,
    #             })
    #             journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
    #             for line in journal_obj.line_ids:
    #                 if line.debit:
    #                     line.with_context(check_move_validity=False).write({
    #                         'debit': abs(avco*i.quantity),
    #                     })
    #                 if line.credit:
    #                     line.with_context(check_move_validity=False).write({
    #                         'credit': abs(avco*i.quantity),
    #                     })
               
                
    
        
    # def perbaikan_valuation(self):
    #     valuation_obj = self.env['stock.valuation.layer'].search([],order='product_id,id desc')
    #     for i in valuation_obj:
    #         if i.value !=0:
    #             if i.stock_move_id.picking_code != 'internal':
    #                 i.sudo().write({
    #                         'value': i.quantity*temp,
    #                     })
    #             if i.stock_move_id.picking_code == None:
    #                 i.sudo().write({
    #                         'value': i.quantity*temp,
    #                     })
    # def perbaikan_unit_cost(self):
    #     valuation_obj = self.env['stock.valuation.layer'].search([],order='product_id,id desc')
    #     for i in valuation_obj:
    #         if i.value !=0:
    #             i.sudo().write({
    #                     'unit_cost': i.value/i.quantity
    #                 })


    # def perbaikan_hpp(self):
    #     svl_obj = self.env['stock.valuation.layer'].search([])

    #     for i in svl_obj:
    #         if i.branch_id.id == 1 and i.stock_move_id.picking_code not in ["internal","incoming"] :
    #             if temp != i.product_id.standard_price_jakarta :
                    
    #                 i.sudo().write({
    #                     'unit_cost': i.product_id.standard_price_jakarta,
    #                     'value': i.product_id.standard_price_jakarta*i.quantity,
    #                 })
    #                 journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
    #                 for line in journal_obj.line_ids:
    #                     if line.debit:
    #                         line.with_context(check_move_validity=False).write({
    #                             'debit': abs(i.product_id.standard_price_jakarta*i.quantity),
    #                         })
    #                     if line.credit:
    #                         line.with_context(check_move_validity=False).write({
    #                             'credit': abs(i.product_id.standard_price_jakarta*i.quantity),
    #                         })
    #                 print(journal_obj.id)
    #         elif i.branch_id.id == 2 and i.stock_move_id.picking_code not in ["internal","incoming"] :
    #             if temp != i.product_id.standard_price_surabaya:
                   
    #                 i.sudo().write({
    #                     'unit_cost': i.product_id.standard_price_surabaya,
    #                     'value': i.product_id.standard_price_surabaya*i.quantity,
    #                 })
    #                 journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
    #                 for line in journal_obj.line_ids:
    #                     if line.debit:
    #                         line.with_context(check_move_validity=False).write({
    #                             'debit': abs(i.product_id.standard_price_surabaya*i.quantity),
    #                         })
    #                     if line.credit:
    #                         line.with_context(check_move_validity=False).write({
    #                             'credit': abs(i.product_id.standard_price_surabaya*i.quantity),
    #                         })
    #         elif i.branch_id.id == 3 and i.stock_move_id.picking_code not in ["internal","incoming"] :
    #             if temp != i.product_id.standard_price_bali:
    #                 i.sudo().write({
    #                     'unit_cost': i.product_id.standard_price_bali,
    #                     'value': i.product_id.standard_price_bali*i.quantity,
    #                 })
    #                 journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
    #                 for line in journal_obj.line_ids:
    #                     if line.debit:
    #                         line.with_context(check_move_validity=False).write({
    #                             'debit': abs(i.product_id.standard_price_bali*i.quantity),
    #                         })
    #                     if line.credit:
    #                         line.with_context(check_move_validity=False).write({
    #                             'credit': abs(i.product_id.standard_price_bali*i.quantity),
    #                         })
    # def perbaikan_hpp2(self):
    #     svl_obj = self.env['stock.valuation.layer'].search([])

    #     for i in svl_obj:
    #         if i.branch_id.id == 1 and i.stock_move_id.location_id.id == 5 :
    #             if temp != i.product_id.standard_price_jakarta :
                    
    #                 i.sudo().write({
    #                     'unit_cost': i.product_id.standard_price_jakarta,
    #                     'value': i.product_id.standard_price_jakarta*i.quantity,
    #                 })
    #                 journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
    #                 for line in journal_obj.line_ids:
    #                     if line.debit:
    #                         line.with_context(check_move_validity=False).write({
    #                             'debit': abs(i.product_id.standard_price_jakarta*i.quantity),
    #                         })
    #                     if line.credit:
    #                         line.with_context(check_move_validity=False).write({
    #                             'credit': abs(i.product_id.standard_price_jakarta*i.quantity),
    #                         })
    #                 print(journal_obj.id)
    #         elif i.branch_id.id == 2 and i.stock_move_id.location_id.id == 5  :
    #             if temp != i.product_id.standard_price_surabaya:
                   
    #                 i.sudo().write({
    #                     'unit_cost': i.product_id.standard_price_surabaya,
    #                     'value': i.product_id.standard_price_surabaya*i.quantity,
    #                 })
    #                 journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
    #                 for line in journal_obj.line_ids:
    #                     if line.debit:
    #                         line.with_context(check_move_validity=False).write({
    #                             'debit': abs(i.product_id.standard_price_surabaya*i.quantity),
    #                         })
    #                     if line.credit:
    #                         line.with_context(check_move_validity=False).write({
    #                             'credit': abs(i.product_id.standard_price_surabaya*i.quantity),
    #                         })
    #         elif i.branch_id.id == 3 and i.stock_move_id.location_id.id == 5  :
    #             if temp != i.product_id.standard_price_bali:
    #                 i.sudo().write({
    #                     'unit_cost': i.product_id.standard_price_bali,
    #                     'value': i.product_id.standard_price_bali*i.quantity,
    #                 })
    #                 journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
    #                 for line in journal_obj.line_ids:
    #                     if line.debit:
    #                         line.with_context(check_move_validity=False).write({
    #                             'debit': abs(i.product_id.standard_price_bali*i.quantity),
    #                         })
    #                     if line.credit:
    #                         line.with_context(check_move_validity=False).write({
    #                             'credit': abs(i.product_id.standard_price_bali*i.quantity),
    #                         })
    def perbaikan_hpp_lanjutan_bali(self):
            
            string_input_with_date = "2023/03/01"
            past = datetime.strptime(string_input_with_date, "%Y/%m/%d")
            valuation_obj = self.env['stock.valuation.layer'].search([],order='product_id,id asc')
            product=[]
            quantity=0
            cost = 0
            temp=0
            for i in valuation_obj:
                if i.branch_id.id == 3:
                    if i.product_id != product:
                        product=i.product_id
                        quantity = i.quantity
                        temp=0
                        cost=i.unit_cost
                        print(i.product_id.name,'1temp',temp,i.unit_cost)
                    else:
                        print(temp,'temp0')
                        quantity += i.quantity
                        if i.create_date > past:
                            if temp == 0:
                                temp =cost
                                print(i.product_id.name,'0temp',temp,i.unit_cost)
                            if i.quantity < 0:
             
                                i.sudo().write({
                                'unit_cost': round(temp,7),
                                'value':round(temp,7)*i.quantity
                                })
                                journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                                for line in journal_obj.line_ids:
                                    if line.debit:
                                        line.with_context(check_move_validity=False).write({
                                            'debit': abs(round(temp,7)*i.quantity),
                                        })
                                    if line.credit:
                                        line.with_context(check_move_validity=False).write({
                                            'credit': abs(round(temp,7)*i.quantity),
                                        })
                                print(i.product_id.name,'2temp',temp,i.unit_cost)
                            if i.quantity > 0:
                                if quantity != 0:
                                    temp = ((round(cost,7)*(quantity-i.quantity))+(round(i.unit_cost,7)*i.quantity))/quantity
                                    if i.unit_cost == 0:
                                        i.sudo().write({
                                        'unit_cost': round(cost,7),
                                        'value':round(cost,7)*i.quantity
                                        })
                                        journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                                        for line in journal_obj.line_ids:
                                            if line.debit:
                                                line.with_context(check_move_validity=False).write({
                                                    'debit': abs(round(cost,7)*i.quantity),
                                                })
                                            if line.credit:
                                                line.with_context(check_move_validity=False).write({
                                                    'credit': abs(round(cost,7)*i.quantity),
                                                })

                                            print(i.product_id.name,'temp',temp,i.unit_cost)
                                else:
                                    temp= round(i.unit_cost,7)
                    cost = i.unit_cost
    def perbaikan_hpp_lanjutan_jakarta(self):
            
            string_input_with_date = "2023/03/01"
            past = datetime.strptime(string_input_with_date, "%Y/%m/%d")
            valuation_obj = self.env['stock.valuation.layer'].search([],order='product_id,id asc')
            product=[]
            quantity=0
            cost = 0
            temp=0
            for i in valuation_obj:
                if i.branch_id.id == 1:
                    if i.product_id != product:
                        product=i.product_id
                        quantity = i.quantity
                        temp=0
                        cost=i.unit_cost
                        print(i.product_id.name,'1temp',temp,i.unit_cost)
                    else:
                        quantity += i.quantity
                        if i.create_date > past:
                            if temp == 0:
                                temp =cost
                                print(i.product_id.name,'0temp',temp,i.unit_cost)
                            if i.quantity < 0:
             
                                i.sudo().write({
                                'unit_cost': round(temp,7),
                                'value':round(temp,7)*i.quantity
                                })
                                journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                                for line in journal_obj.line_ids:
                                    
                                    if line.debit:
                                        line.with_context(check_move_validity=False).write({
                                            'debit': abs(round(temp,7)*i.quantity),
                                        })
                                    if line.credit:
                                        line.with_context(check_move_validity=False).write({
                                            'credit': abs(round(temp,7)*i.quantity),
                                        })
                                  
                            if i.quantity > 0:
                                if quantity != 0:
                                    temp = ((round(cost,7)*(quantity-i.quantity))+(round(i.unit_cost,7)*i.quantity))/quantity
                                    if i.unit_cost == 0:
                                        i.sudo().write({
                                        'unit_cost': round(cost,7),
                                        'value':round(cost,7)*i.quantity
                                        })
                                        journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                                        for line in journal_obj.line_ids:
                                            if line.debit:
                                                line.with_context(check_move_validity=False).write({
                                                    'debit': abs(round(cost,7)*i.quantity),
                                                })
                                            if line.credit:
                                                line.with_context(check_move_validity=False).write({
                                                    'credit': abs(round(cost,7)*i.quantity),
                                                })

                                           
                                else:
                                    temp= round(i.unit_cost,7)
                    cost = i.unit_cost

    def perbaikan_hpp_lanjutan_surabaya(self):
            
            string_input_with_date = "2023/03/01"
            past = datetime.strptime(string_input_with_date, "%Y/%m/%d")
            valuation_obj = self.env['stock.valuation.layer'].search([],order='product_id,id asc')
            product=[]
            quantity=0
            cost = 0
            temp=0
            for i in valuation_obj:
                if i.branch_id.id == 2:
                    if i.product_id != product:
                        product=i.product_id
                        quantity = i.quantity
                        temp=0
                        cost=i.unit_cost
                        print(i.product_id.name,'1temp',temp,i.unit_cost)
                    else:
                        print(temp,'temp0')
                        quantity += i.quantity
                        if i.create_date > past:
                            if temp == 0:
                                temp =cost
                                print(i.product_id.name,'0temp',temp,i.unit_cost)
                            if i.quantity < 0:
             
                                i.sudo().write({
                                'unit_cost': round(temp,7),
                                'value':round(temp,7)*i.quantity
                                })
                                journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                                for line in journal_obj.line_ids:
                                    if line.debit:
                                        line.with_context(check_move_validity=False).write({
                                            'debit': abs(round(temp,7)*i.quantity),
                                        })
                                    if line.credit:
                                        line.with_context(check_move_validity=False).write({
                                            'credit': abs(round(temp,7)*i.quantity),
                                        })
                                print(i.product_id.name,'2temp',temp,i.unit_cost)
                            if i.quantity > 0:
                                if quantity != 0:
                                    temp = ((round(cost,7)*(quantity-i.quantity))+(round(i.unit_cost,7)*i.quantity))/quantity
                                    if i.unit_cost == 0:
                                        i.sudo().write({
                                        'unit_cost': round(cost,7),
                                        'value':round(cost,7)*i.quantity
                                        })
                                        journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                                        for line in journal_obj.line_ids:
                                            if line.debit:
                                                line.with_context(check_move_validity=False).write({
                                                    'debit': abs(round(cost,7)*i.quantity),
                                                })
                                            if line.credit:
                                                line.with_context(check_move_validity=False).write({
                                                    'credit': abs(round(cost,7)*i.quantity),
                                                })

                                            print(i.product_id.name,'temp',temp,i.unit_cost)
                                else:
                                    temp= round(i.unit_cost,7)
                    cost = i.unit_cost
    def perbaikan_hpp_lanjutan_jakarta_mo799(self):
            
            string_input_with_date = "2023/04/01"
            past = datetime.strptime(string_input_with_date, "%Y/%m/%d")
            valuation_obj = self.env['stock.valuation.layer'].search([("product_id","=",2070)],order='product_id,id asc')
            product=[]
            quantity=0
            cost = 0
            temp=0
            for i in valuation_obj:
                print(i.product_id.name)
                if i.branch_id.id == 1:
                    if i.product_id != product:
                        product=i.product_id
                        quantity = i.quantity
                        temp=0
                    else:
                        quantity += i.quantity
                        if i.create_date > past:
                            if temp == 0:
                                temp = (i.value/i.quantity)
          
                            if i.quantity < 0:
                                i.sudo().write({
                                'unit_cost': round(temp,7),
                                'value':round(temp,7)*i.quantity
                                })
                                journal_obj = self.env['account.move'].search([('id','=',i.account_move_id.id)])
                                
                                for line in journal_obj.line_ids:
                                    if line.debit:
                                        line.with_context(check_move_validity=False).write({
                                            'debit': abs(round(temp,7)*i.quantity),
                                        })
                                    if line.credit:
                                        line.with_context(check_move_validity=False).write({
                                            'credit': abs(round(temp,7)*i.quantity),
                                        })
                            if i.quantity > 0:
                                if quantity != 0:
                                    temp = ((round(cost,7)*(quantity-i.quantity))+(round(i.unit_cost,7)*i.quantity))/quantity
                                else:
                                    temp= round(i.unit_cost,7)
                        cost = i.unit_cost


                    



                        
class accountmove(models.Model):
    _inherit = 'account.move'

    
    def reset_to_deraf(self):
        string_input_with_date = "2023/04/01"
        past = datetime.strptime(string_input_with_date, "%Y/%m/%d")
        inv_obj = self.env['account.move'].search([('move_type','=','out_invoice'),("state","!=","cancel"),('date','>',past)])
        for i in inv_obj:
            i.button_draft()
            i.action_post()


    def sinkron_date(self):
        inv_obj = self.env['account.move'].search([('move_type','=','out_invoice'),("state","!=","cancel"),("tanggal_tukar_faktur","!=",False)])
        for i in inv_obj:
            term = i.invoice_payment_term_id.line_ids
            date_due = i.tanggal_tukar_faktur + timedelta(term.days)
            i.invoice_date_due = date_due

    # def sinkron_invoice(self):
    #     inv_obj = self.env['account.move'].search([('move_type','=','out_invoice'),("state","!=","cancel")])
    #     temp=0
    #     for i in inv_obj:
    #         for line in i.line_ids:
    #             if line.account_id.id == line.product_id.
            # for this in do_obj:
            #     for line in i.line_ids:
            #         if line.product_id.id == this.product_id.id:
            #             for lines in this.account_move_ids:
            #                 for ids in lines.line_ids:
            #                     if line.account_id.id == ids.account_id.id:             
            #                         temp=temp+1
            #                         print(line.account_id.id,ids.account_id.id)
                                    
                
            

#######aktifin kalo mau reset to draft
# class accountmove(models.Model):
#     _inherit = 'account.move.line'
#     def remove_move_reconcile(self):
#         """ Undo a reconciliation """
#         return True