import datetime
import string
import random

from oauth2_provider.models import Application
from oauth2_provider.models import AccessToken


class CustomTestUtils(object):
    @staticmethod
    def _create_user(username, password, is_staff=False):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username, "%s@user.com" % username, password, is_staff=is_staff)
        return user

    @staticmethod
    def _create_application(name, user):
        try:
            app = Application.objects.get(name=name)
        except Application.DoesNotExist:
            app = Application.objects.create(
                name=name,
                redirect_uris="http://example.com",
                client_id='client_id',
                client_secret='client_secret',
                client_type=Application.CLIENT_CONFIDENTIAL,
                authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
                user=user,
                skip_authorization=True
            )
        return app

    def _get_access_token(self, user, app, scope='read write update delete'):
        access_token = self.generate_token()
        from django.utils import timezone
        expires = timezone.now() + datetime.timedelta(days=1000)
        access_token_object = AccessToken(user=user, token=access_token, application=app,
                                          expires=expires, scope=scope)
        access_token_object.save()
        return access_token_object

    @staticmethod
    def generate_token():
        size = 30
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        return ''.join(random.choice(chars) for _ in range(size))

    @staticmethod
    def mock_auth(client, access_token):
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
