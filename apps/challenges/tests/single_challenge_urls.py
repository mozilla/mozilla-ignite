from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('challenges.views',
    url(r'$', 'show', name='challenge_show'),
    url(r'entries/$', 'entries_all', name='entries_all'),
    url(r'entries/add/$', 'create_entry', name='entry_create'),
    url(r'entries/(?P<entry_id>\d+)/$', 'entry_show',
        name='entry_show'),
    )
