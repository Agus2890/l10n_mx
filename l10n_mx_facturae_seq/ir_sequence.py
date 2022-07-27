# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo import release


class IrSequenceApproval(models.Model):
    _name = 'ir.sequence.approval'

    _rec_name = 'approval_number'

    def _get_type(self):
        types = []
        return types

    company_id = fields.Many2one('res.company', _('Company'), required=True,
        help='Company where will add this approval')
    approval_number = fields.Char(u'Approval Number', size=64,
        required=True, help='Name of the type of Electronic Invoice to \
        configure')
    serie = fields.Char(u'Serie of Folios', size=12, required=False,
        help="With which report to SAT, example. FA (for Invoices), NC \
        (For Invoice Refund)")
    approval_year = fields.Char('Year Approval', size=32, required=True,
        help='Year of approval from the Certificate')
    number_start = fields.Integer(u'Since', required=False,
        help='Initial Number of folios purchased')
    number_end = fields.Integer(u'Until', required=True,
        help='Finished Number of folios purchased')
    sequence_id = fields.Many2one('ir.sequence', u'Sequence',
        required=True, ondelete='cascade', help='Sequence where will add \
        this approval')
    type = fields.Selection(_get_type, 'Type', type='char', size=64,
        required=True, help="Type of Electronic Invoice")

    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company').\
            _company_default_get(cr, uid, 'ir.sequence.approval', context=c),
    }

    _sql_constraints = [
        ('number_start', 'CHECK (number_start < number_end )',
         _('The initial number (Since), must be less to end (Until)!')),
        ('number_end', 'CHECK (number_end > number_start )',
         _('The finished number (Until), must be higher to initial (Since)!')),
    ]

    def _check_numbers_range(self):
        query = """SELECT approval_1.id AS id1, approval_2.id AS id2--\
            approval_1.number_start, approval_1.number_end, approval_2.\
            number_start, approval_2.number_end, *
            FROM ir_sequence_approval approval_1
            INNER JOIN (
                SELECT *
                FROM ir_sequence_approval
               ) approval_2
               ON approval_2.sequence_id = approval_1.sequence_id
              AND approval_2.id <> approval_1.id
            WHERE approval_1.sequence_id = %d
              AND ( approval_1.number_start between approval_2.number_start \
                and approval_2.number_end )
            LIMIT 1
        """ % (self.sequence_id.id)
        cr.execute(query)
        res = cr.dictfetchone()
        if res:
            return False
        return True

    _constraints = [
        (_check_numbers_range, 'Error ! There ranges of numbers underhand between approvals.', \
            ['sequence_id', 'number_start', 'number_end'])
    ]


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    def copy(self):
        if context is None:
            context = {}
        if not default:
            default = {}
        default = default.copy()
        default['approval_ids'] = False
        return super(IrSequence, self).copy()

    def _get_current_approval(self):
        res = {}
        for id in ids:
            res[id] = False
        approval_obj = self.env['ir.sequence.approval']
        for sequence in self:
            number_work = context.get(
                'number_work', None) or sequence.number_next
            approval_ids = approval_obj.search([
                ('sequence_id', '=', sequence.id),
                ('number_start', '<=', number_work),
                ('number_end', '>=', number_work)],
                limit=1)
            approval_id = approval_ids and approval_ids[0] or False
            res[sequence.id] = approval_id
        return res

    approval_ids = fields.One2many('ir.sequence.approval', 'sequence_id',
            string='Sequences', help='Approvals in this Sequence'),
    approval_id = fields.Many2one(compute='_get_current_approval', relation='ir.sequence.approval',
            string='Approval Current', help='Approval active in this sequence'),
        # 'expiring_rate': fields.integer('Tolerancia de Advertencia', help='Tolerancia Cantidad Advertencia de Folios Aprobados por Terminarse'),
        # s'expiring'

    def _check_sequence_number_diff(self):
        if context is None:
            context = {}
        # ahorita nadie manda a llamar esta funcion, ya que no existen los
        # warnings, como tal en OpenERP.
        sequence_number_diff_rate = 10
        sequences = self.browse(cr, uid, ids, context=context)
        data = {}
        for sequence in sequences:
            if sequence.approval_id:
                sequence_number_diff = sequence.approval_id.number_end - \
                    sequence.next_number
                if sequence_number_diff <= sequence_number_diff_rate:
                    warning = {
                        'title': 'Caution sequences!',
                        'message': 'The folios are close to finish, of the sequence %s' % (
                            sequence.name)
                    }
                    data = {'warning': warning}
                    break
        return data

    def get_id(self, cr, uid, sequence_id, test='id=%s', context=None):
        if context is None:
            context = {}
        if release.version < '6':
            # inicia copy & paste, de una seccion de la funcion original
            if test not in ('id=%s', 'code=%s'):
                raise ValueError('invalid test')
            cr.execute('select id from ir_sequence where ' + test + ' and active=%s', (
                sequence_id, True,))
            res = cr.dictfetchone()
            # Finaliza copy & paste, de una seccion de la funcion original
            if res:
                sequence = self.browse(cr, uid, res['id'], context=context)
                if sequence.approval_ids:
                    approval_obj = self.pool.get('ir.sequence.approval')
                    approval_id = self._get_current_approval(cr, uid, [
                        sequence.id], field_names=None, arg=False,
                        context=context)[sequence.id]
                    approval_id = approval_id and approval_obj.browse(
                        cr, uid, [approval_id], context=context)[0] or False
                    if not approval_id:
                        raise models.except_models(
                            _('Error !'),
                            _('No hay una aprobacion valida de folios.')
                        )
            return super(IrSequence, self).get_id(cr, uid, sequence_id, test)
        else:
            # inicia copy & paste, de una seccion de la funcion original
            if test == 'id=%s':
                test = 'id'
            if test == 'code=%s':
                test = 'code'
            assert test in ('code', 'id')
            company_id = self.pool.get('res.users').read(cr, uid, uid, [
                'company_id'], context=context)['company_id'][0] or None
            cr.execute('''SELECT id, number_next, prefix, suffix, padding
                          FROM ir_sequence
                          WHERE %s=%%s
                           AND active=true
                           AND (company_id = %%s or company_id is NULL)
                          ORDER BY company_id, id
                          --FOR UPDATE NOWAIT''' % test,
                      (sequence_id, company_id))
            res = cr.dictfetchone()
            # Finaliza copy & paste, de una seccion de la funcion original
            if res:
                sequence = self.browse(cr, uid, res['id'], context=context)
                if sequence.approval_ids:
                    approval_obj = self.pool.get('ir.sequence.approval')
                    approval_id = self._get_current_approval(cr, uid, [
                        sequence.id], field_names=None, arg=False,
                        context=context)[sequence.id]
                    approval_id = approval_id and approval_obj.browse(
                        cr, uid, [approval_id], context=context)[0] or False
                    if not approval_id:
                        raise models.except_models(
                            _('Error !'),
                            _('No hay una aprobacion valida de folios.')
                        )
                    return super(IrSequence, self).get_id(cr, uid, res['id'], 'id')
            return super(IrSequence, self).get_id(cr, uid, sequence_id, test)
