from django.conf.urls import url
from . import views
from django.conf.urls import include

urlpatterns=[
    url(r'^test/monitor/$', views.test_monitor, name='test_monitor'),
    url(r'test/mcamera/$', views.test_mcamera, name='test_mcamera'),
    # url(r'^srs_validation/on_publish/$', views.srs_on_publish, name='on_publish'),
    # url(r'^srs_validation/on_play/$', views.srs_on_play, name='on_play')
    # url(r'^api-auth/', include('rest_framework.urls',
    #                            namespace='rest_framework')),
    url(r'^api/v1/', include('app.api_v1_urls'))
]