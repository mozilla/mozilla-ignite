from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

admin.autodiscover()

_ignite_kwargs = {'project': settings.IGNITE_PROJECT_SLUG,
                  'slug': settings.IGNITE_CHALLENGE_SLUG}

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^browserid/', include('django_browserid.urls')),
    url(r'^$', 'challenges.views.show', kwargs=_ignite_kwargs, name='challenge_show'),
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
