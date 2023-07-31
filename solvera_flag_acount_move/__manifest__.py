# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Flag Account Move',
    'category': 'Contact',
    'author': 'Michael',
    'version': '1.0',
    'website': 'http://www.solvera.id/',
    'description': """
       Base For Any Project SOlvera
    """,
    'data': [
        # 'security/ir.model.access.csv',
        'views/invoice_view.xml',


    ],
    "depends": [
        "account",
    ],
    'installable': True,
    "images":['static/logo.png'],
}
