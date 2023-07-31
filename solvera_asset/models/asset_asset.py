
import datetime
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero

class Assetasset(models.Model):
    _inherit = 'account.asset.asset'

    date_collection = fields.Datetime(string="Date Collection",readonly=False)
    def _get_default_branch(self):
        branch = False
        if len(self.env.user.branch_ids) == 1:
            branch = self.env.user.branch_id
            return branch

    def _get_branch_domain(self):
        """methode to get branch domain"""
        company = self.env.company
        branch_ids = self.env.user.branch_ids
        branch = branch_ids.filtered(
            lambda branch: branch.company_id == company)
        return [('id', 'in', branch.ids)]

    branch_id = fields.Many2one('res.branch', string='Branch', store=True,
                                readonly=False,
                                default=_get_default_branch,
                                domain=_get_branch_domain)
    
class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    def create_move(self, post_move=True):
        created_moves = self.env['account.move']
        prec = self.env['decimal.precision'].precision_get('Account')
        if self.mapped('move_id'):
            raise UserError(_(
                'This depreciation is already linked to a journal entry! Please post or delete it.'))
        for line in self:
            category_id = line.asset_id.category_id
            depreciation_date = self.env.context.get(
                'depreciation_date') or line.depreciation_date or fields.Date.context_today(
                self)
            company_currency = line.asset_id.company_id.currency_id
            current_currency = line.asset_id.currency_id
            branch_id = line.asset_id.branch_id.id
            amount = current_currency.with_context(
                date=depreciation_date).compute(line.amount, company_currency)
            asset_name = line.asset_id.name + ' (%s/%s)' % (
            line.sequence, len(line.asset_id.depreciation_line_ids))
            partner = self.env['res.partner']._find_accounting_partner(
                line.asset_id.partner_id)
            move_line_1 = {
                'name': asset_name,
                'account_id': category_id.account_depreciation_id.id,
                'debit': 0.0 if float_compare(amount, 0.0,
                                              precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0,
                                                  precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id,
                'partner_id': partner.id,
                'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'sale' else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
            }
            move_line_2 = {
                'name': asset_name,
                'account_id': category_id.account_depreciation_expense_id.id,
                'credit': 0.0 if float_compare(amount, 0.0,
                                               precision_digits=prec) > 0 else -amount,
                'debit': amount if float_compare(amount, 0.0,
                                                 precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id,
                'partner_id': partner.id,
                'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'purchase' else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and line.amount or 0.0,
            }
            if branch_id:
                move_vals = {
                    'ref': line.asset_id.code,
                    'date': depreciation_date or False,
                    'journal_id': category_id.journal_id.id,
                    'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
                    'branch_id': branch_id
                }
            else:
                move_vals = {
                    'ref': line.asset_id.code,
                    'date': depreciation_date or False,
                    'journal_id': category_id.journal_id.id,
                    'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
                }
            move = self.env['account.move'].create(move_vals)
            line.write({'move_id': move.id, 'move_check': True})
            created_moves |= move

        if post_move and created_moves:
            created_moves.filtered(lambda m: any(
                m.asset_depreciation_ids.mapped(
                    'asset_id.category_id.open_asset'))).post()
        return [x.id for x in created_moves]
   