from odoo import models, fields, api,  _
from ast import literal_eval


class CustomCompany(models.Model):
    _inherit = 'res.company'

    is_hide_all_menu = fields.Boolean('lock')

    @api.onchange('is_hide_all_menu')
    def expired(self,*get):

        query = """select id
                    FROM ir_ui_menu
                    WHERE parent_id is null"""
        self.env.cr.execute(query)
        res = self.env.cr.fetchall()
        menu_ids = []
        for x in res:
            menu_ids.append(x)
        menu_ids = self.env['ir.ui.menu'].browse(menu_ids)

        for this in self:
            for menu in menu_ids:
                menu.active = False if this.is_hide_all_menu else True
        
        return True
