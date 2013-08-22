# coding: utf-8
import unittest

from os.path import dirname, join

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

from pyramid import paster, testing
from pyramid.security import has_permission

from intranet3.models import Base, DBSession


ROOT_PATH = dirname(__file__)
setting_file = join(ROOT_PATH, "../../etc/", "test.ini")
settings = paster.get_appsettings(setting_file)
engine = engine_from_config(settings, prefix='sqlalchemy.')

DBSession.configure(bind=engine)
Base.metadata.drop_all(engine)  # Drop
Base.metadata.create_all(engine)  # Create


class Request(testing.DummyRequest):

    def __init__(self):
        self.tmpl_ctx = {}

        super(Request, self).__init__()

    def has_perm(self, perm):
        return has_permission(perm, self.context, self)


class BaseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = engine
        cls.Session = sessionmaker()

    def setUp(self):
        connection = self.engine.connect()

        # begin a non-ORM transaction
        self.trans = connection.begin()

        # bind an individual Session to the connection
        DBSession.configure(bind=connection)
        self.session = self.Session(bind=connection)
        Base.session = self.session

        self.config = testing.setUp()
        self.request = Request()

    def tearDown(self):
        testing.tearDown()
        self.trans.rollback()
        self.session.close()
