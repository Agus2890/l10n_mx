# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'FacturaE Notes Invoice',
    'name': 'l10n_mx_notes_invoice',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/Mexico',
    'description': """
This module add field for notes in company for electrinic invoice report
    """,
    'website': 'www.mikrointeracciones.com.mx', 
    'license': 'AGPL-3',
    'depends' : ['base'],
    'init_xml': [],
    'demo_xml': [],
    'update_xml': [
        'views/res_company_view.xml',
    ],
    'installable': True,
    'active': False,
}
