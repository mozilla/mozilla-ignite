from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^(?P<project>[\w-]+)/participation/(?P<slug>[\w-]+)/$',
        'participation.views.show',
        name='participation_show'),
    url(r'^(?P<project>[\w-]+)/participation/(?P<slug>[\w-]+)/entries/$',
        'participation.views.entries_all',
        name='entries_all'),
    url(r'^(?P<project>[\w-]+)/participation/(?P<slug>[\w-]+)/entries/add/$',
        'participation.views.create_entry',
        name='participation_create'),
    url(r'^(?P<project>[\w-]+)/participation/(?P<slug>[\w-]+)/entries/(?P<entry_id>\d+)/$',
        'participation.views.entry_show',
        name='entry_show')
    )
