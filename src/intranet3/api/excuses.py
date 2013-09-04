# coding: utf-8
import iso8601

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config

from intranet3.utils import excuses
from intranet3.utils.views import ApiView


@view_config(route_name="api_excuses", permission="freelancer",
             renderer='json')
class Excuses(ApiView):

    def protect(self):
        date_str = self.request.GET.get('date')
        if date_str is not None:
            try:
                date = iso8601.parse_date(date_str).date()
            except iso8601.ParseError:
                raise HTTPBadRequest("Accepted date format ISO-8601: YYYY-MM-DD/YYYMMDD")
        else:
            raise HTTPBadRequest("Date param is required")

        self.v['date'] = date

    def get(self):
        return dict(
            justification_status=excuses.wrongtime_status(self.v['date'], self.request.user.id),
        )        
