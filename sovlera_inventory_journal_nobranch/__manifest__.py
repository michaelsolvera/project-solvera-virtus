# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Solvera Product Sample',
    'category': 'Stock',
    'author': 'Michael',
    'version': '1.0',
    'website': 'http://www.solvera.id/',
    'description': """
      Product Sample
    """,
    'data': [
        'security/ir.model.access.csv',
	    'views/stock_inventory_view.xml',
        # 'views/product_categ.xml',

    ],
    "depends": [
        "stock","solvera_contact_information"
    ],
    'installable': True,
    "images":['static/logo.png'],
}
