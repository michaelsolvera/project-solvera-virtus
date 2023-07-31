# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

{
    'name': 'Deposit Management',
    'version': '14.0.0.1',
    'summary': '''
        Deposit Management in Odoo allows users to add deposit product
        on sale and purchase order and also refund deposit product.
    ''',
    'category': 'Sales',
    'description': """
        Deposit Management in Odoo.
        Deposit based sales order and purchase orders.
        Deposit refund on sales and purchase.
        Multiple reports for deposit order.
        Reports with date filters and customer filters.
    """,
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'http://www.caretit.com',
    'support': 'sales@caretit.com',
    'depends': ['base', 'sale_management' ,'sale_stock', 'purchase_stock'],
    'data': [
        'security/ir.model.access.csv',
        'report/report_template.xml',
        'report/report.xml',
        'wizard/picking_return.xml',
        'wizard/sale_report_wiz.xml',
        'wizard/purchase_report_wiz.xml',
        'views/product_template_view.xml',
        'views/deposit_order_view.xml',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
        'views/stock_view.xml',
        'views/account_move.xml'
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'auto_install': False,
}
