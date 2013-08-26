# coding: utf-8
import transaction

from tests.factory import FactoryMixin
from .base import ApiBaseTest


class ApiTimeCollectionTestCase(FactoryMixin, ApiBaseTest):

    def test_api_view_not_logged(self):
        response = self.app.get('/api/times')
        self.assertNotEqual(response.status_int, 200)
        self.assertEqual(response.status_int, 302)

        response = response.follow()
        self.assertEqual(response.request.path, "/auth/logout_view")

    def test_get_method_protect(self):
        user = self.create_user(groups=['user'])
        freelancer = self.create_user(is_freelancer=True, groups=['freelancer'])
        transaction.commit()

        # Login as user      
        self.login(user.name, user.email)

        response = self.app.get(
            '/api/times',
            extra_environ=self.request
        )
        self.assertEqual(response.status_int, 200)
        
        # User checks another user `TimeEntries`
        response = self.app.get(
            '/api/times',
            {'user_id': freelancer.id},
            extra_environ=self.request
        )
        self.assertEqual(response.status_int, 200)

        # Log as Freelancer
        self.app.get('/auth/logout')
        self.login(freelancer.name, freelancer.email)

        # User is `freelancer`       
        response = self.app.get(
            '/api/times',
            extra_environ=self.request
        )
        self.assertEqual(response.status_int, 200)
        
        # Freelancer checks another user `TimeEntries`
        response = self.app.get(
            '/api/times',
            {'user_id': user.id},
            extra_environ=self.request,
            expect_errors=True
        )
        self.assertEqual(response.status_int, 403)

    def test_post_method_protect(self):
        user = self.create_user(groups=['user'])
        freelancer = self.create_user(is_freelancer=True, groups=['freelancer'])
        client = self.create_client()
        tracker = self.create_tracker()
        project = self.create_project(user=user, client=client, tracker=tracker)
        transaction.commit()

        # Valid JSON
        test_data = {
            'project_id': project.id,
            'ticket_id': 3,
            'time': '2.5',
            'description': "Planning meeting",
            'timer': False,
            'add_to_harvest': False,
            'start_timer': False,
        }

        self.login(user.name, user.email)
        # Post as `user`
        response = self.app.post_json(
            '/api/times',
            params=test_data,
            extra_environ=self.request,
            expect_errors=True
        )
        self.assertEqual(response.status_int, 201)

        # Post for another user
        response = self.app.post_json(
            '/api/times?user_id=%s' % freelancer.id,
            params=test_data,
            extra_environ=self.request,
            expect_errors=True
        )
        self.assertEqual(response.status_int, 403)

    def test_get_response(self):
        user = self.create_user(groups=['user'])
        client = self.create_client()
        tracker = self.create_tracker()
        project = self.create_project(user=user, client=client, tracker=tracker)
        transaction.commit()
        
        # Test Data
        test_data = {
            'project_id': project.id,
            'ticket_id': 3,
            'time': '2.5',
            'description': "Planning meeting",
            'timer': False,
            'add_to_harvest': False,
            'start_timer': False,
        }

        self.login(user.name, user.email)
        # Add Data
        self.app.post_json(
            '/api/times',
            params=test_data,
            extra_environ=self.request,
            expect_errors=True
        )
        # Get Data
        response = self.app.get(
            '/api/times',
            extra_environ=self.request
        )

        data = response.json

        self.assertEqual(response.status_int, 200)
        self.assertIsInstance(data['entries'], list)

        entry = data['entries'][0]
        # Len of entries should be
        self.assertEqual(len(data['entries']), 1)
        self.assertEqual(entry['project']['client_name'], client.name)
        self.assertEqual(entry['project']['project_name'], project.name)
        
        # Default tracker set as bugzilla
        self.assertEqual(entry['tracker_url'], "%s/show_bug.cgi?id=%s"% (tracker.url, 3))
        self.assertEqual(entry['time'], 2.5)
        self.assertEqual(entry['desc'], "Planning meeting")
        self.assertEqual(entry['ticket_id'], 3)

    def test_post_response(self):
        user = self.create_user(groups=['user'])
        client = self.create_client()
        tracker = self.create_tracker()
        project = self.create_project(user=user, client=client, tracker=tracker)
        transaction.commit()

        # Test Data
        test_data = {
            'project_id': project.id,
            'ticket_id': 3,
            'time': '2.5',
            'description': "Planning meeting",
            'timer': False,
            'add_to_harvest': False,
            'start_timer': False,
        }

        self.login(user.name, user.email)
        # Add Data

        response = self.app.post_json(
            '/api/times',
            params=test_data,
            extra_environ=self.request,
            expect_errors=True
        )

        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.json['message'], "OK")

    def test_invalid_data(self):
        user = self.create_user(groups=['user'])
        client = self.create_client()
        tracker = self.create_tracker()
        project = self.create_project(user=user, client=client, tracker=tracker)
        transaction.commit()

        self.login(user.name, user.email)

        test_data = {
            'project_id': project.id,
            'time': 3,
            'description': "Planning meeting",
            'timer': False,
            'add_to_harvest': False,
            'start_timer': False,
        }

        response = self.app.post_json(
            '/api/times',
            params=test_data,
            extra_environ=self.request,
            expect_errors=True
        )

        data = response.json['message']
        self.assertEqual(response.status_int, 400)
        self.assertEqual(data['ticket_id'], "Ticket should be String or Int")

        test_data = {
            'time': 3,
            'ticket_id': 3,
            'description': "Planning meeting",
            'timer': False,
            'add_to_harvest': False,
            'start_timer': False,
        }

        response = self.app.post_json(
            '/api/times',
            params=test_data,
            extra_environ=self.request,
            expect_errors=True
        )

        data = response.json['message']
        self.assertEqual(response.status_int, 400)
        self.assertEqual(data['project_id'], "Required")

    def test_timeobject_colander(self):
        """
            Test `intranet3.schemas.times.TimeObject`
        """
        user = self.create_user(groups=['user'])
        client = self.create_client()
        tracker = self.create_tracker()
        project = self.create_project(user=user, client=client, tracker=tracker)
        transaction.commit()

        self.login(user.name, user.email)

        test_data = {
            'project_id': project.id,
            'ticket_id': 3,
            'time': '2.5',
            'description': "Planning meeting",
            'timer': False,
            'add_to_harvest': False,
            'start_timer': False,
        }

        response = self.app.post_json(
            '/api/times',
            params=test_data,
            extra_environ=self.request,
            expect_errors=True
        )
        self.assertEqual(response.status_int, 201)

        test_data.update({'time': 2.6})

        response = self.app.post_json(
            '/api/times',
            params=test_data,
            extra_environ=self.request,
            expect_errors=True
        )

        self.assertEqual(response.status_int, 201)

        # Format HH:MM
        test_data.update({'time': "1:22"})

        response = self.app.post_json(
            '/api/times',
            params=test_data,
            extra_environ=self.request,
            expect_errors=True
        )
        self.assertEqual(response.status_int, 201)

        # Check values
        response = self.app.get(
            '/api/times',
            extra_environ=self.request,
            expect_errors=True
        )

        entries = response.json['entries']
        for entry in entries:
            self.assertIn(entry['time'], [2.5, 2.6, 1.36666666666667])