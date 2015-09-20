from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^hotels$', views.hotels, name='hotels'),
]
