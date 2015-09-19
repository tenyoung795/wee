import datetime
from django.conf import settings
from django.contrib.auth.models import User
import requests

class UberAuthenticationBackend:
    """Upon a Uber user logging in, Uber should redirect to an endpoint
    invoking this backend."""

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, django_request):
        access_token_response = requests.post(
            'https://login.uber.com/oauth/token',
            params={
                'client_secret': settings.UBER_CLIENT_SECRET,
                'client_id': settings.UBER_CLIENT_ID,
                'grant_type': 'authorization_code',
                'redirect_uri': django_request.build_absolute_uri(
                    django_request.path),
                'code': django_request.GET['code'],
            })
        access_token_response.raise_for_status()
        access_token_json = access_token_response.json()
        access_token = access_token_json['access_token']

        try:
            profile_response = requests.get(
                settings.UBER_API_HOST + '/v1/me',
                headers={'Authorization': 'Bearer ' + access_token})
            profile_response.raise_for_status()
            profile = profile_response.json()
            uuid = profile['uuid']

            session = django_request.session
            session['access_token'] = access_token
            session['refresh_token'] = access_token_json['refresh_token']
            # TODO: Ensure no locale problems are possible.
            response_unix_s = datetime.datetime.strptime(
                access_token_response.headers['Date'],
                '%a, %d %b %Y %H:%M:%S GMT').timestamp()
            expires_in_s = access_token_json['expires_in']
            session['token_refresh_unix_s'] = response_unix_s + expires_in_s

            try:
                return User.objects.get(username=uuid)
            except User.DoesNotExist:
                user = User.objects.create_user(uuid)
                user.save()
                return user
        except:
            # Let's be respectful of the user's privacy and revoke the token.
            revoke_response = requests.get(
                'https://login.uber.com/oauth/revoke',
                params={
                    'client_secret': settings.UBER_CLIENT_SECRET,
                    'client_id': settings.UBER_CLIENT_ID,
                    'token': access_token
                })
            if revoke_response.status_code != requests.codes.ok:
                # TODO: That's unfortunate; log current time and status code
                # and pray no bastard stole the token.
                pass
            raise
