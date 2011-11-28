from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import redirect_to
from jingo.views import direct_to_template


admin.autodiscover()

_ignite_kwargs = {'project': settings.IGNITE_PROJECT_SLUG,
                  'slug': settings.IGNITE_CHALLENGE_SLUG}

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^browserid/', include('django_browserid.urls')),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', kwargs={'next_page': '/'}, name='logout'),
    url(r'^accounts/login/$', 'jingo.render', kwargs={'template': 'registration/login.html'}, name='login'),
    url(r'^$', 'ignite.views.splash', kwargs=_ignite_kwargs, name='challenge_show'),
    (r'', include('users.urls')),
    # The /ideas/ URL will become available in the application phase
    url(r'^ideas/$', redirect_to, kwargs={'url': '/', 'permanent': False}),
    url(r'^ideas/(?P<entry_id>\d+)/$', 'challenges.views.entry_show', kwargs=_ignite_kwargs, name='entry_show'),
    url(r'^ideas/(?P<pk>\d+)/edit/$', 'challenges.views.entry_edit', kwargs=_ignite_kwargs, name='entry_edit'),
    url(r'^entries/add/$', 'challenges.views.create_entry', kwargs=_ignite_kwargs, name='create_entry'),
)

# Handle 404 and 500 errors
handler404 = 'innovate.views.handle404'
handler500 = 'innovate.views.handle500'

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
