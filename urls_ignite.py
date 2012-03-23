from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.http import HttpResponseRedirect

from challenges.models import SubmissionParent
from voting.views import vote_on_object


admin.autodiscover()

_ignite_kwargs = {'project': settings.IGNITE_PROJECT_SLUG,
                  'slug': settings.IGNITE_CHALLENGE_SLUG}

vote_dict = {
    'model': SubmissionParent,
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
    url(r'^ideas/winning/$', 'challenges.views.entries_winning', kwargs=_ignite_kwargs, name='entries_winning'),
    url(r'^ideas/judged/$', 'challenges.views.entries_judged', kwargs=_ignite_kwargs, name='entries_judged'),
    url(r'^ideas/list/(?P<category>[\w-]+)/$', 'challenges.views.entries_category', kwargs=_ignite_kwargs, name='entries_for_category'),
    url(r'^ideas/list/$', 'challenges.views.entries_all', kwargs=_ignite_kwargs, name='entries_all'),
    url(r'^ideas/(?P<entry_id>\d+)/$', 'challenges.views.entry_show', kwargs=_ignite_kwargs, name='entry_show'),
    url(r'^ideas/(?P<pk>\d+)/judgement/$', 'challenges.views.entry_judge', kwargs=_ignite_kwargs, name='entry_judge'),
    url(r'^ideas/(?P<pk>\d+)/edit/$', 'challenges.views.entry_edit', kwargs=_ignite_kwargs, name='entry_edit'),
    url(r'^ideas/(?P<pk>\d+)/delete/$', 'challenges.views.entry_delete', kwargs=_ignite_kwargs, name='entry_delete'),
    url(r'^ideas/vote/(?P<object_id>\d+)/(?P<direction>up|clear)/?$',
        vote_on_object, vote_dict, name='entry_vote'),
    url(r'^ideas/add/$', 'challenges.views.create_entry', kwargs=_ignite_kwargs, name='create_entry'),
    url(r'^judges/$', 'ignite.views.judges', kwargs=_ignite_kwargs, name='our_judges'),
    url(r'^about/$', 'ignite.views.about', kwargs=_ignite_kwargs,  name='about_ignite'),
    url(r'^terms/$', 'ignite.views.terms', kwargs=_ignite_kwargs,  name='terms_conditions')
)

urlpatterns += patterns(
    'challenges.views',
    url(r'^ideas/v/(?P<entry_id>\d+)/$', 'entry_version',
        kwargs=_ignite_kwargs, name='entry_version'),
    )

urlpatterns += patterns(
    '',
    (r'^resources/', include('resources.urls', namespace='resources')),
    (r'^award/', include('awards.urls', namespace='awards'), _ignite_kwargs),
    )


if settings.DEVELOPMENT_PHASE:
    urlpatterns += patterns(
        '',
        (r'^booking/', include('timeslot.urls', namespace='timeslot'),),
        (r'^webcast/', include('webcast.urls', namespace='webcast'),),
        )

# Handle 404 and 500 errors
handler404 = 'ignite.views.fail'
handler500 = 'ignite.views.app_fail'

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
