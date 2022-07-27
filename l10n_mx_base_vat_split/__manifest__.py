# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'VAT Number Split',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',    
    'category': 'Localization/México',
    'description': """
Split VAT Number to l10n-VAT in a new field calculated.
    """,
    'website': 'http://mikrointeracciones.com.mx',    
    'depends': ['base_vat'],
    'data': [
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}

