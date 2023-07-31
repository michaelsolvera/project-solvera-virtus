# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Solvera Create Bill From Invoice Line',
    'category': 'Account',
    'author': 'Michael',
    'version': '1.0',
    'website': 'http://www.solvera.id/',
    'description': """
       solvy Custom Report
    """,
    'data': [
        'views/invoice_view.xml',
        'views/product_views.xml',

    ],
    "depends": [
        "account"
    ],
    'installable': True,
    "images":['static/logo.png'],
}
