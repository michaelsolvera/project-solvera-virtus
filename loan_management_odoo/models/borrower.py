from odoo import models, fields, api

class borrower(models.Model):
    _name = 'borrower.borrower'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'created_date'
    _description = 'Borrowers Informations'


    name = fields.Char(string='Full name', required=True, track_visibility='always')
    title = fields.Selection([
        ('mr', 'Mr.'), ('mrs', 'Mrs.'), ('miss', 'Miss.'), ('ms', 'Ms.'), ('dr', 'Dr.'), ('prof', 'Prof.'), ('rev', 'Rev.')])
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')])
    created_date = fields.Datetime(string="Registered on", required=False, default=lambda self: fields.datetime.now())
    borrower_dob = fields.Date(string="Date of Birth")
    address = fields.Char(string="Address")
    mobile = fields.Integer(string="Work Mobile",size=10, track_visibility='always')
    phone = fields.Integer(string="Work Phone", size=10, track_visibility='always')
    email = fields.Char(string="Email Address")
    unique_id = fields.Char(string="Borrower no")
    working_status = fields.Selection([
        ('unemployed', 'Unemployeed'),
        ('employee', 'Employee'),
        ('govt_employee', 'Govement Employee'),
        ('prvt_employee', 'Private Sector Employee'),
        ('business_owner', 'Business owner'),
        ('student', 'Student'),
        ('pensioner', 'Pensioner'),
    ])
    borrower_photo = fields.Binary(string="Borrower Photo")
    description = fields.Text(string="Remarks")
    borrower_file = fields.Binary(string="Borrower File")
    #loan_officer = 
