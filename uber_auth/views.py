from django.conf import settings
from django.contrib import auth
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.http import QueryDict
from django.shortcuts import redirect

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
    return HttpResponse('Hello, %s' % request.user.get_username())
