# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools.translate import _
#from odoo import fields, orm


class ImportInfo(models.Model):
    _name = "import.info"
    _description = "Information about customs"
    _order = 'name asc'

    # def _get_audit(self, cr, uid, ids, field_name, arg, context=None):
    #     if context is None:
    #         context = {}
    #     result = {}
    #     for i in ids:
    #         chain = ''
    #         for p in self.browse(cr, uid, [i], context)[0].product_info_ids:
    #             if not self.browse(cr, uid, [i], context)[0].supplier_id.id in [
    #                 s.name.id for s in p.product_id.seller_ids]:
    #                 chain2 = '\nVerify the product: %s the Supplier on this document is not related to this product.\n' % p.product_id.name
    #                 chain = chain + chain2
    #         result[i] = chain
    #     return result


    name = fields.Char(
            string='Number of Operation', help="Transaction Number"
        )
    customs = fields.Char(
            string='Customs', size=64,
            help="What Customs was used in your country for import this lot"
                 " (Generally it is a legal information)"
        )
    date = fields.Date(
            string='Date',
            help="Date of Custom and Import Information (In Document)"
        )
    lot_ids = fields.One2many(
            'stock.production.lot', 'import_id', string='Production Lot'
        )
    rate = fields.Float(
            string='Exchange Rate', required=True, digits=(16, 4),
            help='Exchange rate informed on Custom House when the transaction'
                 ' was approved'
        )
    company_id = fields.Many2one('res.company', string='Company',
                                 required=True, readonly=True,
                                 #states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env['res.company'].\
                                    _company_default_get('import.info'),                                
                                 help="Company related to this document.")
    # company_id = fields.Many2one('res.company', 'Company',
    #                              required=True, readonly=True,
    #                              states={'draft': [('readonly', False)]},
    #                              default=lambda self: self.env['res.company'].\
    #                                 _company_default_get('tax.certificate'))

    supplier_id = fields.Many2one(
            'res.partner', String='Supplier', select=1,
            help="Partner to whom bought the product on this document."
        )
    invoice_ids = fields.Many2many(
            'account.invoice', 'account_invoice_rel',
            'import_id', 'invoice_id', string='Invoices Related'
        )
    product_info_ids = fields.One2many(
            'product.import.info', 'import_id',
            string='Products Info', required=False
        )
    audit_note = fields.Text(
            #_get_audit, method=True, type='text', string=_('Audit Notes')
            string=_('Audit Notes')
        )

    # _defaults = {
    #     'company_id': lambda s, cr, uid, c: s.pool.get('res.company').
    #     _company_default_get(cr, uid, 'import.info', context=c)
    # }
