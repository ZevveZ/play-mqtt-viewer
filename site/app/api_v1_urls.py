from django.conf.urls import url
from app import views

urlpatterns=[
    url(r'^$', views.api_root, name = 'api_root'),
    url(r'^users/$', views.users, name = 'users'),
    url(r'^users/(\w+)/$', views.user, name='user'),
    url(r'^users/(\w+)/([0-9]+)/$', views.userdevice, name = 'userdevice'),
    url(r'^session/$', views.session, name='session'),
    url(r'^devices/$', views.devices, name='devices'),
    url(r'^devices/([0-9]+)/$', views.device, name='device'),
    url(r'^sensors/$', views.sensors, name = 'sensors'),
]