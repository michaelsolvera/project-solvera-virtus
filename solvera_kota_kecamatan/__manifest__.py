# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Solvera Kota, Kecamatan, Kelurahan',
    'category': 'Contacts',
    'author': 'Michael',
    'version': '1.0',
    'website': 'http://www.solvera.id/',
    'description': """
       Identifikasi Kota dan kecamatan Di indonesia
    """,
    'data': [
        'views/city_view.xml',
        'views/res_view.xml',
    ],
    'depends': [
                'base',
                'contacts',

                ],
    'installable': True,
    "images":['static/logo.png'],
}
