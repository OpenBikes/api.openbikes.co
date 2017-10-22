from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^archives/$', views.archives, name='archives'),
    url(r'^archives/[a-z,-]+-(?P<city_id>[0-9]+)/$', views.city_archives,
        name='city_archives')
]
