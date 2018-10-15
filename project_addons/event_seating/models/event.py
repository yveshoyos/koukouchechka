# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.http_routing.models.ir_http import slug, slugify
import json


class EventEvent(models.Model):
    _inherit = 'event.event'

    theater_id = fields.Many2one('event.theater', string='Theater')

    def open_website_set_seats_url(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/event_seating/set_seats/%s' % slug(self),
            'target': 'self',
        }

    def open_website_display_seats_url(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/event_seating/display_seats/%s' % slug(self),
            'target': 'self',
        }

    @api.multi
    def get_registrations_json(self):
        self.ensure_one()
        res = {}
        for registration in self.registration_ids:
            res[registration.id] = registration.get_registration_data()
        return json.dumps(res)


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    seat_ids = fields.One2many('event.registration.seat', 'registration_id', string='Seats')
    seats_count = fields.Integer(string='Number of seats', compute='_get_seats_count')

    @api.one
    @api.depends('seat_ids', 'seat_ids.registration_id')
    def _get_seats_count(self):
        self.seats_count = len(self.seat_ids)

    @api.multi
    def get_registration_data(self):
        self.ensure_one()
        return  {
            'id': self.id,
            'name': self.name,
            'date': self.date_open,
            'qty': self.qty,
            'seats_count': self.seats_count,
            'seats': [seat.label for seat in self.seat_ids],
        }

    @api.multi
    def assign_seats(self, seats_label):
        self.ensure_one()
        seats = self.env['event.theater.seat'].search([('theater_id', '=', self.event_id.id), ('label', 'in', seats_label)])
        if len(seats_label) != len(seats):
            raise ValidationError(_("Some seats couldn't be found. Please check given labels."))
        for seat in seats:
            self.env['event.registration.seat'].create({
                'registration_id': self.id,
                'seat_id': seat.id
            })
        self.check_seats()

    @api.multi
    def unassign_seats(self, seats_label):
        self.ensure_one()
        seats = self.seat_ids.filtered(lambda r: r.seat_id.label in seats_label)
        if len(seats_label) != len(seats):
            raise ValidationError(_("Some seats couldn't be found. Please check given labels."))
        seats.unlink()

    @api.multi
    def unassign_all_seats(self):
        self.ensure_one()
        self.seat_ids.unlink()

    @api.one
    @api.constrains('seat_ids')
    def check_seats(self):
        if len(self.seat_ids) > self.qty:
            raise ValidationError(_('There is to much assigned seats than booked seats.'))


class EventRegistrationSeat(models.Model):
    _name = 'event.registration.seat'

    registration_id = fields.Many2one('event.registration', string="Registration", required=True)
    event_id = fields.Many2one('event.event', string="Event", related='registration_id.event_id', readonly=True, store=True)
    seat_id = fields.Many2one('event.theater.seat', string='Seat', required=True)
    label = fields.Char(string='Label', related='seat_id.label', readonly=True, store=True)

    @api.one
    @api.constrains('registration_id', 'seat_id')
    def check_disposition_and_names(self):
        if self.registration_id.event_id.theater_id.id != self.seat_id.theater_id.id:
            raise ValidationError(_('Seat is not linked to the same theater than the one in the event.'))

    _sql_constraints = [
        ('unique_seat_event', 'UNIQUE(event_id, seat_id)', 'A seat can only be used once by event'),
    ]
