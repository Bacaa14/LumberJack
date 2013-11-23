from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from django.contrib import admin
admin.autodiscover()
home = RedirectView.as_view(url='/', permanent=False)
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'lumberjack.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^admin/', include(admin.site.urls)),
    url(r'^seduction/', include('seduction.urls')),
    (r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^$', 'lumberjack.views.index', name='index'),
    url(r'^accounts/profile', home),
    url(r'^users/', home),
)
