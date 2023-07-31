# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools # type: ignore
from odoo.osv import expression  # type: ignore
from odoo.exceptions import UserError, ValidationError  # type: ignore



class ServiceType(models.Model):
    _name = 'service.type'

    name = fields.Char(string='Name', required=True)

    def unlink(self):
        for record in self:
            if record.name:
                used = self.env['account.move'].search_count([('service_type_id', '=', record.id)])
                if used > 0:
                    raise ValidationError("Cannot delete this record as the field is being used in another model.")
        return super(ServiceType, self).unlink()

class FromToLocation(models.Model):
    _name = 'location.master'
    _rec_name = 'complete_name'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True)

    @api.depends('name','code')
    def _compute_complete_name(self):
        for record in self:
            record.complete_name =  f"{record.name} -[{record.code}]"

    def unlink(self):
        for record in self:
            if record.complete_name:
                used = self.env['account.move'].search_count([('from_id', '=', record.id)])
                if used > 0:
                    raise ValidationError("Cannot delete this record as the field is being used in another model.")
        return super(FromToLocation, self).unlink()


class AgentMaster(models.Model):
    _name = 'agent.master'

    name = fields.Char(string='Name', required=True)

    def unlink(self):
        for record in self:
            if record.name:
                used = self.env['account.move'].search_count([('agent_id', '=', record.id)])
                if used > 0:
                    raise ValidationError("Cannot delete this record as the field is being used in another model.")
        return super(AgentMaster, self).unlink()

