from django.conf.urls import patterns, url
from portal import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='portal'),
)