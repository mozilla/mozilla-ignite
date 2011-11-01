from django.conf.urls.defaults import patterns, url

PATH_PREFIX = r'^(?P<project>[\w-]+)/challenges/(?P<slug>[\w-]+)/'

urlpatterns = patterns('challenges.views',
    url(PATH_PREFIX + r'$', 'show', name='challenge_show'),
    url(PATH_PREFIX + r'entries/$', 'entries_all', name='entries_all'),
    url(PATH_PREFIX + r'entries/add/$', 'create_entry', name='entry_create'),
    url(PATH_PREFIX + r'entries/(?P<entry_id>\d+)/$', 'entry_show',
        name='entry_show'),
    )
