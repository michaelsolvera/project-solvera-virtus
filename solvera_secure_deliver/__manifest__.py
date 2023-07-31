# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Solvera Secure Deliver',
    'category': 'stock',
    'author': 'Michael',
    'version': '1.0',
    'website': 'http://www.solvera.id/',
    'description': """
      add on asset date collector
    """,
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/asset_views.xml',

    ],
    "depends": [
        "stock","solvera_contact_tukar_faktur"
    ],
    'installable': True,
    "images":['static/logo.png'],
}
