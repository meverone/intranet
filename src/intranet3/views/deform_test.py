# coding: utf-8
import datetime

import colander
import deform

from jinja2.filters import do_mark_safe

from pyramid.i18n import TranslationStringFactory
from pyramid.view import view_config

from intranet3 import helpers as h
from intranet3.forms.times import EmployeeChoices
from intranet3.forms.project import ProjectChoices
from intranet3.utils.views import BaseView

_ = TranslationStringFactory('intranet3')


def get_choices(generator):
    choices = []
    for item in generator:
        value, label = item
        choices.append((value, label))

    return choices

class DateRange(object):

    format = "%Y-%m-%d"

    def serialize(self, node, cstruct):
        start, end = cstruct
        return "%s - %s" % (start.strftime(self.format), end.strftime(self.format))

    def deserialize(self, node, cstruct):
        try:
            start, end = cstruct.split(' - ')
        except (ValueError, TypeError):
            colander.Invalid(node, "Dates have to splitted by ` - `")

        try:
            start = datetime.datetime.strptime(start, self.format).date()
            end = datetime.datetime.strptime(end, self.format).date()
        except ValueError:
            colander.Invalid(node, 'Not a valid date value')
        else:
            return [start, end]


class TicketTypeMapping(colander.Schema):
    group_by_user = colander.SchemaNode(colander.Boolean(), label=_('Group by employee'), default=True)
    group_by_project = colander.SchemaNode(colander.Boolean(), label=_('Group by project'), default=True)
    group_by_bugs = colander.SchemaNode(colander.Boolean(), label=_('Group by bugs'), default=True)
    group_by_client = colander.SchemaNode(colander.Boolean(), label=_('Group by client'), default=True)

class AddTime(colander.MappingSchema):

    ticket_values = [
        ('all','All'),
        ('without_bug_only','Without bugs only'),
        ('meetings_only','Meetings only'),
    ]

    date_range = colander.SchemaNode(
        DateRange(),
        default=h.start_end_month(datetime.date.today()),
        widget=deform.widget.TextInputWidget(css_class="daterange")
    )
    projects = colander.SchemaNode(
        colander.Set(),
        label=_('Projects'),
        widget=deform.widget.SelectWidget(
            values=get_choices(ProjectChoices(skip_inactive=True)),
            css_class="jq-multisel",
            multiple=True),
    )
    employees = colander.SchemaNode(
        colander.Set(),
        label=_('Employees'),
        widget=deform.widget.SelectWidget(values=get_choices(EmployeeChoices()),
                                          css_class="jq-multisel",
                                          multiple=True)
    )

    Group_by = TicketTypeMapping()

    ticket_choices = colander.SchemaNode(
        colander.String(),
        validator=colander.OneOf([x[0] for x in ticket_values]),
        widget=deform.widget.RadioChoiceWidget(values=ticket_values, css_class="radio-choice"),
        label=_('Tickets'),
        default='all',
    )
    bigger_than = colander.SchemaNode(colander.Integer(), default=0)

@view_config(route_name="deform_test")
class Add(BaseView):
    def get(self):
        schema = AddTime()
        form = deform.Form(schema, buttons=('submit',))
        controls = self.request.GET.items()

        try:
            appstruct = form.validate(controls)
        except deform.ValidationFailure:
            return dict(form=form.render(), res=form.get_widget_resources())

        return dict(form=form.render())
