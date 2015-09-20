import datetime
from django.conf import settings
from django.contrib import auth
from django.contrib import sessions
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.http import QueryDict
from django.shortcuts import redirect
from django.utils import timezone
import requests
from wee_app import models

def login(request):
    query = QueryDict(mutable=True)
    query.update({
        'response_type': 'code',
        'client_id': settings.UBER_CLIENT_ID,
        'scope': 'profile request',
        # TODO: Default redirect to /
        'state': request.GET.get('next', '/accounts/hello')
    })
    return redirect(
        'https://login.uber.com/oauth/authorize'
        + '?' + query.urlencode())

def redirect_uber(request):
    # TODO: Handle exception
    user = authenticate(django_request=request)
    auth.login(request, user)
    return redirect(request.GET['state'])

# TODO: Remove when ready
def hello(request):
    pickup, _ = models.Point.objects.get_or_create(
        latitude=40.719786, longitude=-73.854608)
    destination, _ = models.Point.objects.get_or_create(
        latitude=40.6413111, longitude=-73.7781391)

    res = requests.get(settings.UBER_API_HOST + '/v1/products',
        params={'latitude': pickup.latitude, 'longitude': pickup.longitude},
        headers={'Authorization': 'Bearer ' + request.session['access_token']})
    res.raise_for_status()
    product = res.json()['products'][0]

    req = models.PlannedUberRequest(
        session=sessions.models.Session(pk=request.session.session_key),
        product_id=product['product_id'],
        pickup=pickup, destination=destination,
        request_timestamp=timezone.now() + datetime.timedelta(seconds=1))
    req.save()

    return HttpResponse(
        'Hello, %s; I shall request %s, a %s, in less than 1 second' % (
            request.user.get_username(),
            product['product_id'], product['display_name']))
