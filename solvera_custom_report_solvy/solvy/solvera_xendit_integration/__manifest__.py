# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Database Manager',
    'category': 'Database',
    'author': 'Michael',
    'version': '1.0',
    'website': 'http://www.solvera.id/',
    'description': """
       For create new database for client
    """,
    'data': [

        'views/res_partner_view.xml',

    ],
    'depends': [

       'website',
                ],
    'installable': True,
    "images":['static/logo.png'],
}
