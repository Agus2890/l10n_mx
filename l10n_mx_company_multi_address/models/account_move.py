# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('company_id')
    def _get_emitter_invoice(self):
        res = {}
        # _logger.warning(
        #     'The  company_emitter_id field is depreciated  you '
        #     'should use instead company_id'
        # )
        # for rec in self:
        #     res[rec.id] = rec.company_id.id
        return res

    def _get_address_issued_invoice(self):
        # res = self.env['res.company']._company_default_get('account.invoice')
        # return res
        pass

    address_issued_id = fields.Many2one('res.partner', string='Address Issued Invoice',
            help='This address will be used as address that issued '
            'for electronic invoice',
            default=_get_address_issued_invoice)

    company_emitter_id = fields.Many2one(compute='_get_emitter_invoice',
            comodel_name='res.company', string='Company Emitter Invoice',
            help='This company will be used as emitter company in '
            'he electronic invoice')

    # @api.onchange('journal_id')
    # def onchange_journal_id(self):
    #     res = super(AccountInvoice, self).onchange_journal_id()
    #     address_id = journal_id and self.env['account.journal'].browse(journal_id) or False
    #     if address_id and address_id.address_invoice_company_id:
    #         result['value'].update({'address_invoice_company_id': address_id.address_invoice_company_id.id})
    #     if address_id and address_id.company2_id:
    #         res['value'].update({'company2_id': address_id.company2_id.id})
    #     return res
