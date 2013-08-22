# coding: utf-8
from pyramid import testing

from intranet3.api.times import TimeCollection
from intranet3.utils.request import Request

from tests.factory import FactoryMixin

from .base import BaseTestCase


class BugViewTestCase(FactoryMixin, BaseTestCase):
    """
        TODO:
        Dodać sprawdzanie uprawnień (?)
    """
    def test_time_view(self):
        user = self.create_user(groups=[])
        request = self.request
        request.db_session = self.session
        request.method = "GET"
        request.user = user
        request.context = testing.DummyResource()

        # GET Method
        response = TimeCollection(request.context, request).__call__()
