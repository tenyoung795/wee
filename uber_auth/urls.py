from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login$', views.login, name='login'),
    url(r'^redirect-uber$', views.redirect_uber, name='redirect_uber'),
    # TODO: Remove when ready
    url(r'^hello$', views.hello, name='hello'),
]
