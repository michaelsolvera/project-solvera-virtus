from odoo import fields,models,api
from datetime import datetime,date,timedelta
from odoo.exceptions import UserError
from num2words import num2words

class ProductProduct(models.Model):
    _inherit = "product.product"

    partner_id = fields.Many2one('res.partner', string='Vendor', help="Select a Vendor")

class ProductTemplate(models.Model):
    _inherit = "product.template"

    partner_id = fields.Many2one('res.partner', string='Vendor', help="Select a Vendor",related='product_variant_id.partner_id'
                                 ,readonly=False)
    