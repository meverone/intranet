# coding: utf-8
import unittest

from os.path import dirname, join

from mock import patch

from webtest import TestApp

from pyramid import paster
from pyramid import testing

from intranet3 import main
from intranet3.models import Base, DBSession

from tests.mocks import MockOAuth2FlowSampleData, MockApplicationConfig, mock_get

ROOT_PATH = dirname(__file__)
setting_file = join(ROOT_PATH, "../../etc/", "test.ini")
settings = paster.get_appsettings(setting_file)
application = main(None, **settings)


class ApiBaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = application
        cls.session = DBSession()
        Base.metadata.create_all()

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        Base.metadata.drop_all()

    def setUp(self):
        self.app = TestApp(self.app)
        self.config = testing.setUp()
        Base.metadata.create_all()
     
    def login(self, name, email):
        with patch("intranet3.views.auth.requests.get") as get:
            get.return_value = mock_get(name, email)
            with patch("intranet3.views.auth.OAuth2WebServerFlow.step2_exchange") as flow:
                flow.return_value = MockOAuth2FlowSampleData()
                with patch("intranet3.views.auth.ApplicationConfig") as config:
                    config.return_value = MockApplicationConfig()

                    self.app.get('/auth/callback')

    @property
    def request(self):
        return {
            'REMOTE_ADDR': "127.0.0.1"
        }
