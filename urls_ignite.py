from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.http import HttpResponseRedirect

from challenges.models import SubmissionParent
from voting.views import vote_on_object


from funfactory.monkeypatches import patch
patch()

admin.autodiscover()

_ignite_kwargs = {
    'project': settings.IGNITE_PROJECT_SLUG,
    'slug': settings.IGNITE_CHALLENGE_SLUG
    }

vote_dict = {
    'model': SubmissionParent,
    'template_object_name': 'submission',
    'allow_xmlhttprequest': True,
}

urlpatterns = patterns(
    '',
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', kwargs={'next_page': '/'}, name='logout'),
    url(r'^accounts/login/$', 'jingo.render', kwargs={'template': 'registration/login.html'}, name='login'),
    url(r'^$', 'ignite.views.splash', kwargs=_ignite_kwargs, name='challenge_show'),
    url(r'^ideas/vote/(?P<object_id>\d+)/(?P<direction>up|clear)/?$',
        vote_on_object, vote_dict, name='entry_vote'),
    url(r'^judges/$', 'ignite.views.judges', kwargs=_ignite_kwargs, name='our_judges'),
    url(r'^about/$', 'ignite.views.about', kwargs=_ignite_kwargs,  name='about_ignite'),
    url(r'^terms/$', 'ignite.views.terms', kwargs=_ignite_kwargs,  name='terms_conditions'),
    url(r'^terms_development/$', 'ignite.views.terms_development', kwargs=_ignite_kwargs,  name='terms_conditions_development'),
)


pattern = '(?P<phase>(ideas|apps))'

urlpatterns += patterns(
    'challenges.views',
    url(r'^%s/add/$' % pattern, 'create_entry', kwargs=_ignite_kwargs,
        name='create_entry'),
    url(r'^%s/(?P<entry_id>\d+)/$' % pattern, 'entry_show',
        kwargs=_ignite_kwargs, name='entry_show'),
    url(r'^%s/list/$' % pattern, 'entries_all', kwargs=_ignite_kwargs,
        name='entries_all'),
    url(r'^%s/list/(?P<category>[\w-]+)/$' % pattern, 'entries_category',
        kwargs=_ignite_kwargs, name='entries_for_category'),
    url(r'^%s/winners/$' % pattern, 'entries_winning',
        kwargs=_ignite_kwargs, name='entries_winning'),
    url(r'^%s/(?P<pk>\d+)/edit/$' % pattern, 'entry_edit',
        kwargs=_ignite_kwargs, name='entry_edit'),
    url(r'^%s/(?P<pk>\d+)/delete/$' % pattern, 'entry_delete',
        kwargs=_ignite_kwargs, name='entry_delete'),
)


urlpatterns += patterns(
    'challenges.views',
    # url(r'^ideas/v/(?P<entry_id>\d+)/$', 'entry_version',
    #     kwargs=_ignite_kwargs, name='entry_version'),
    url(r'^submissions/(?P<entry_id>\d+)/help/$', 'entry_help',
        kwargs=_ignite_kwargs, name='entry_help'),
    url(r'^submissions/help-wanted/$', 'entry_help_list',
        kwargs=_ignite_kwargs, name='entry_help_list'),
    # Judging views
    url(r'^submission/(?P<pk>\d+)/judgement/$', 'entry_judge',
        kwargs=_ignite_kwargs, name='entry_judge'),
    url(r'^dashboard/$', 'entries_assigned',
        kwargs=_ignite_kwargs, name='entries_assigned'),
    url(r'^submissions/green-lit/$', 'entries_winning',
        kwargs=_ignite_kwargs, name='entries_winning'),
    url(r'^challenges/export/$', 'export_challenges',
        name='export_challenges'),
)


urlpatterns += patterns(
    '',
    (r'^resources/', include('ignite_resources.urls', namespace='resources')),
    (r'^award/', include('awards.urls', namespace='awards'), _ignite_kwargs),
    (r'^booking/', include('timeslot.urls', namespace='timeslot'),),
    (r'^webcast/', include('webcast.urls', namespace='webcast'),),
    (r'^search/', include('search.urls', namespace='search'),),
    (r'^admin/', include(admin.site.urls)),
    (r'^browserid/', include('django_browserid.urls')),
    (r'', include('users.urls')),
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
if settings.DEBUG and 'debug_toolbar_user_panel' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'', include('debug_toolbar_user_panel.urls')),
        )
