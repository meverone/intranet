# coding: utf-8
from pyramid.view import view_config
from pyramid.response import Response

from intranet3.models import ApplicationConfig, Project, Tracker, TrackerCredentials
from intranet3.models.project import SelectorMapping
from intranet3.log import DEBUG_LOG, WARN_LOG, EXCEPTION_LOG, INFO_LOG
from intranet3.utils.mail import CustomClientFactory, MailerPOP3Client, ssl, reactor
from intranet3.utils.views import CronView


LOG = INFO_LOG(__name__)
EXCEPTION = EXCEPTION_LOG(__name__)
WARN = WARN_LOG(__name__)
DEBUG = DEBUG_LOG(__name__)


@view_config(route_name="cron_mail_get")
class Sync(CronView):

    MAX_BUSY_CALLS = 3
    POP3_SERVER = 'pop.gmail.com'
    POP3_PORT = 995
    context_factory = ssl.ClientContextFactory()

    def mark_not_busy(self):
        if not self.busy:
            WARN(u'Tried to unmark an already unmarked Mail Checker')
        else:
            self.busy = False
            LOG(u'Marked Mail Check as not busy anymore')

    def action(self):
        self.busy = False
        self.busy_calls = 0

        config = ApplicationConfig.get_current_config(allow_empty=True)
        if config is None:
            WARN(u'Application config not found, emails cannot be checked')
            return self.mark_not_busy()
        trackers = dict(
            (tracker.mailer, tracker)
                for tracker in Tracker.query.filter(Tracker.mailer != None).filter(Tracker.mailer != '')
        )
        if not len(trackers):
            WARN(u'No trackers have mailers configured, email will not be checked')
            return self.mark_not_busy()

        username = config.google_user_email.encode('utf-8')
        password = config.google_user_password.encode('utf-8')

        # TODO
        logins_mappings = dict(
            (tracker.id, TrackerCredentials.get_logins_mapping(tracker))
                for tracker in trackers.itervalues()
        )
        selector_mappings = dict(
            (tracker.id, SelectorMapping(tracker))
                for tracker in trackers.itervalues()
        )

        # find all projects connected to the tracker
        projects = dict(
            (project.id, project)
                for project in Project.query.all()
        )

        # all pre-conditions should be checked by now

        # start fetching
        f = CustomClientFactory(username, password, self.mark_not_busy,
            trackers, logins_mappings, projects, selector_mappings)
        f.protocol = MailerPOP3Client
        reactor.connectSSL(self.POP3_SERVER, self.POP3_PORT, f, self.context_factory)

        return Response('OK')
