# -*- coding: utf-8 -*-
#########################################################################
#                                                                       #
#   STRANBYS.COM                                                        #
#                                              #
#   GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3)                         #
#                                                                       #
#########################################################################

{
   'name': 'Solvera Accounting Sales',
    'category': 'Asset',
    'author': 'Michael',
    'version': '1.0',
    'website': 'http://www.solvera.id/',
    'description': """
      Accounting But Sales
    """,
    "depends": ['base', 'account',"base_accounting_kit"],
    "data": [
        'security/travels_security.xml',
        'views/menus.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
