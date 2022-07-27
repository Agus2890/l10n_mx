# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Agregado de Moneda, Clabe Interbancaria y los Ultimos Cuatro Dígitos de la Cuenta a res.partner.bank',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/México',
    'description' : """This module add currency, field clabe interbancaria & the last 4 digits of the account to model res.partner.bank
    """,
    'website': 'www.mikrointeracciones.com.mx',
    'license': 'AGPL-3',
    'depends' : ['account'],
    'init_xml' : [],
    'demo_xml' : [],
    'update_xml' : [
    	'views/res_bank_view.xml',
    ],
    'installable' : True,
    'active' : False,
}
