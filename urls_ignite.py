from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.views.generic.simple import redirect_to
from jingo.views import direct_to_template
from voting.views import vote_on_object

from challenges.models import Submission

admin.autodiscover()

_ignite_kwargs = {'project': settings.IGNITE_PROJECT_SLUG,
                  'slug': settings.IGNITE_CHALLENGE_SLUG}

vote_dict = {
    'model': Submission,
    'template_object_name': 'submission',
    'allow_xmlhttprequest': True,
}

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^browserid/', include('django_browserid.urls')),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', kwargs={'next_page': '/'}, name='logout'),
    url(r'^accounts/login/$', 'jingo.render', kwargs={'template': 'registration/login.html'}, name='login'),
    url(r'^$', 'ignite.views.splash', kwargs=_ignite_kwargs, name='challenge_show'),
    (r'', include('users.urls')),
    # The /ideas/ URL will become available in the application phase
    url(r'^ideas/assigned/$', 'challenges.views.entries_assigned', kwargs=_ignite_kwargs, name='entries_assigned'),
    url(r'^ideas/list/(?P<category>[\w-]+)/$', 'challenges.views.entries_category', kwargs=_ignite_kwargs, name='entries_for_category'),
    url(r'^ideas/list/$', 'challenges.views.entries_all', kwargs=_ignite_kwargs, name='entries_all'),
    url(r'^ideas/(?P<entry_id>\d+)/$', 'challenges.views.entry_show', kwargs=_ignite_kwargs, name='entry_show'),
    url(r'^ideas/(?P<pk>\d+)/judgement/$', 'challenges.views.entry_judge', kwargs=_ignite_kwargs, name='entry_judge'),
    url(r'^ideas/(?P<pk>\d+)/edit/$', 'challenges.views.entry_edit', kwargs=_ignite_kwargs, name='entry_edit'),
    url(r'^ideas/(?P<pk>\d+)/delete/$', 'challenges.views.entry_delete', kwargs=_ignite_kwargs, name='entry_delete'),
    url(r'^ideas/vote/(?P<object_id>\d+)/(?P<direction>up|clear)/?$',
        vote_on_object, vote_dict, name='entry_vote'),
    url(r'^ideas/add/$', 'challenges.views.create_entry', kwargs=_ignite_kwargs, name='create_entry'),
    # quick redirect to send all requests to /blog/ to the blog itself
    url(r'^blog/', lambda x: HttpResponseRedirect('https://mozillaignite.org/blog/')),
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
