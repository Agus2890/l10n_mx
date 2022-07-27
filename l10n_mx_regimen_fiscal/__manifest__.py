# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Agrega el Regimen Fiscal al partner',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/México',
    'description': """
Add 'Regimen Fiscal' to partner, it's used by 
l10n_mx_facturae module
    """,
    'website': 'http://mikrointeracciones.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'account', 
        'l10n_mx_facturae_groups',
    ],
    'demo': [],
    'data': [
        #'security/regimen_fiscal.xml',
        #'security/ir.model.access.csv',
        'views/regimen_fiscal.xml',
        'data/regimen_fiscal_data.xml',
    ],
    'installable': True,   
    'active': False,
}
