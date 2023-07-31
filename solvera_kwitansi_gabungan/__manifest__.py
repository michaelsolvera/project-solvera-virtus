# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Kwitansi Gabungan',
    'category': 'Contact',
    'author': 'Michael',
    'version': '1.0',
    'website': 'http://www.solvera.id/',
    'description': """
       Kwitansi gabungan
    """,
    'data': [
        'security/ir.model.access.csv',
        'wizard/tukar_faktur.xml',
        'reports/reports.xml',
        'reports/report_kwitansi_gabungan.xml',
    ],
    "depends": [
        "sale","account"
    ],
    'installable': True,
    "images":['static/logo.png'],
}
