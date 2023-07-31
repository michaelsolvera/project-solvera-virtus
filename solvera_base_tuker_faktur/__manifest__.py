# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Custom Contact tukar faktur',
    'category': 'Contact',
    'author': 'Michael',
    'version': '1.0',
    'website': 'http://www.solvera.id/',
    'description': """
       Base For Any Project SOlvera
    """,
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner_view.xml',

    ],
    "depends": [
        "solvera_contact_tukar_faktur_nobranch",
    ],
    'installable': True,
    "images":['static/logo.png'],
}
