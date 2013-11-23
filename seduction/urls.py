from django.conf.urls import patterns, url

from seduction import views

urlpatterns = patterns('',
    url(r'^(?P<shift_id>\d+)/$', views.viewShift, name='view'),
    url(r'^(?P<shift_id>\d+)/edit/$', views.editShift, name='edit'),
    url(r'^create/$', views.createShift, name='create'),
    url(r'^instantiate/$', views.instantiateShift, name='instantiate'),
    url(r'^logShift/(?P<shift_id>\d+)$', views.logShift, name='logShift'),
)


