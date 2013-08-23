# coding: utf-8
from intranet3 import models

class FactoryMixin(object):

    # Current state of counter
    cid = 1 # Client
    uid = 1 # User
    pid = 1 # Project
    tid = 1 # Tracker

    def create_user(self, name="", is_freelancer=False, domain="stxnext.pl", groups=[]):
        username = name or "user_%s" % self.uid
        
        user = models.User(
            email="%s@%s" % (username, domain),
            name=username,
            location="wroclaw",
            refresh_token='test_token',
            freelancer=is_freelancer
        )
        user.groups = groups

        self.session.add(user)
        self.session.flush()

        if name == "":
            self.uid += 1

        return user

    def create_users(self, is_freelancer=False, amount=1, domain="stxnext.pl", groups=[]):
        return [self.create_user(is_freelancer, domain, groups) for i in xrange(0, amount)]

    def create_client(self, name=""):
        user = self.create_user(groups=['user'])
        client = models.Client(
            coordinator_id=user.id,
            name="client_%s"% self.cid,
            color="red?",
            emails="blabla@gmail.com"
        )
        self.session.add(client)
        self.session.flush()

        self.cid += 1

        return client

    def create_tracker(self, name=""):
        name = name or "tracker_%s" % self.tid
        tracker = models.Tracker(
            type="bugzilla",
            name=name,
            url="http://%s.name" % name
        )

        self.session.add(tracker)
        self.session.flush()

        self.tid += 1

        return tracker

    def create_project(self, name="", user=None, client=None, tracker=None):
        if user is None or client is None or tracker is None:
            raise AttributeError()

        name = name or "project_%s"% self.pid

        project = models.Project(
            name=name,
            coordinator_id=user.id,
            client_id=client.id,
            tracker_id=tracker.id,
            active=True,
        )

        self.session.add(project)
        self.session.flush()

        self.pid += 1

        return project
