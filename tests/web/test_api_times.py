# coding: utf-8
import transaction

from tests.factory import FactoryMixin
from .base import ApiBaseTest


class ApiTimeCollectionPermissionTestCase(FactoryMixin, ApiBaseTest):

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
        response = self.app.post(
            '/api/times',
            params=test_data,
            extra_environ=self.request,
            expect_errors=True
        )
        self.assertEqual(response.status_int, 201)

        # Post for another user
        response = self.app.post(
            '/api/times?user_id=%s' % freelancer.id,
            params=test_data,
            extra_environ=self.request,
            expect_errors=True
        )
        self.assertEqual(response.status_int, 403)
