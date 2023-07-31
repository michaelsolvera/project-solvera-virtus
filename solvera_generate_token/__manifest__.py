# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Solvera Generate Token',
    'category': 'Custom Field',
    'author': 'Michael',
    'version': '1.0',
    'website': 'http://www.solvera.id/',
    'description': """
       Solvera Generate Token
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',

    ],
    'depends': [
                'contacts',

                ],
    'installable': True,
    "images":['/static/logo.png'],
}
