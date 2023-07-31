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
        # 'security/ir.model.access.csv',
        'views/web_login.xml',
        'views/web_lupapassword.xml',
        'views/web_pendaftaran.xml',
        'views/res_partner_view.xml',
        'views/payment_success.xml',
        'data/email_template.xml',

    ],
    'depends': [

       'website',
                ],
    'installable': True,
    "images":['static/logo.png'],
}
