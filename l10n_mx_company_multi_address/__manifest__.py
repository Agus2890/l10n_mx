# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Multiaddress para una misma compañia',
    'version': '1.0',
    'author': 'Mikrointeracciones de México', 
    'category': 'Localization/México',
    'description': """
This module allows the management of multiaddress for 'factura electronica' whitout multicompany scheme
    """,
    'website': 'http://mikrointeracciones.com.mx',
    'license': 'AGPL-3',
    'depends': ['base','account'],
    'demo': [],
    'data': [
        #'security/ir.model.access.csv',
        'views/account_move_view.xml',
        #'ir_sequence_view.xml',
        #'res_company_view6.xml',
        #'invoice_view.xml',
        'views/res_company_view.xml',
        'views/account_journal_view.xml',
        #'partner_address_view.xml',
    ],
    'installable': True,
    'active': False,
}
