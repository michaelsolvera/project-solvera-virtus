# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProductTemplateDeposit(models.Model):
    _inherit = 'product.template'

    is_deposit = fields.Boolean(string='Is a Deposit', default=False)
    deposit_product_id = fields.Many2one(
        'product.product', string='Deposit Product',
        domain=[('is_deposit','=', True)], help='Link your deposit product')
    sale_deposit_price = fields.Float(
        string='Sales Deposit Amount', help='set deposit product sales price')
    purchase_deposit_price = fields.Float(
        string='Purchase Deposit Amount', help='set deposit product cost')
    ##container fields
    is_container = fields.Boolean(string='Is a Container', default=False)
    container_qty = fields.Float(string='Contained Quantity', default=12,
                                    help='set Contained Quantity of product')
    container_product_id = fields.Many2one(
        'product.product', string='Container Product',
        domain=[('is_container','=', True)], help='Link your Container product')
    sale_container_price = fields.Float(
        string='Sales Container Amount', help='set container product sales price')
    purchase_container_price = fields.Float(
        string='Purchase Container Amount', help='set container product cost')

    _sql_constraints = [
        ('default_code', 'unique(default_code)', "An Internal Reference can only be assigned to one product !"),
    ]

    @api.constrains('is_deposit', 'is_container', 'type')
    def check_product_type(self):
        '''It will raise warning if product is deposit/container but not consumable type.'''
        if self.is_deposit or self.is_container:
            if not self.type == 'consu':
                raise ValidationError(_('Deposit/Container product type must be consumable type!'))

    def write(self, vals):
        '''Raise validation if user change deposit/container product.'''
        res = super(ProductTemplateDeposit, self).write(vals)
        if vals.get('is_deposit') == False or vals.get('is_container') == False:
            raise ValidationError(_('Cannot change Deposit/Container product!'))
        return res

    @api.onchange('deposit_product_id')
    def onchange_deposit_product_id(self):
        '''update product price for deposit product.'''
        product = self.deposit_product_id
        if product:
            self.write({
                'sale_deposit_price': product.list_price,
                'purchase_deposit_price': product.standard_price
            })

    @api.onchange('container_product_id')
    def onchange_container_product_id(self):
        '''update product price for container product.'''
        product = self.container_product_id
        if product:
            self.write({
                'sale_container_price': product.list_price,
                'purchase_container_price': product.standard_price,
                'container_qty': product.container_qty
            })
