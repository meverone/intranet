# coding: utf-8
import transaction

from tests.factory import FactoryMixin
from .base import ApiBaseTest


class ApiBugTestCase(FactoryMixin, ApiBaseTest):

    def test_api_bug_view_not_logged(self):
        response = self.app.get('/api/bugs')
        self.assertNotEqual(response.status_int, 200)
        self.assertEqual(response.status_int, 302)

        response = response.follow()
        self.assertEqual(response.request.path, "/auth/logout_view")

    def test_response(self):
        user = self.create_user(groups=['user'])
        transaction.commit()

        self.login(user.name, user.email)
        
        response = self.app.get('/api/bugs', extra_environ=self.request)
        self.assertEqual(response.status_int, 200)
        self.assertNotEqual(response.json.get('bugs'), None)

        self.assertIsInstance(response.json.get('bugs'), list)

    def test_permissions(self):
        user = self.create_user(groups=['user'])
        _user = self.create_user()
        transaction.commit()

        self.login(user.name, user.email)

        response = self.app.get('/api/bugs', extra_environ=self.request)
        self.assertEqual(response.status_int, 200)

        # Log user without persmclea
        self.app.get('/auth/logout')
        self.login(_user.name, _user.email)

        response = self.app.get('/api/bugs', extra_environ=self.request,
                                expect_errors=True)
        self.assertEqual(response.status_int, 403)
