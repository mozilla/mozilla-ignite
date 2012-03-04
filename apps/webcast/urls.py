from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'webcast.views',
    url(r'^$', 'webcast_list', {'slug': 'all'}, name='object_list'),
    url(r'^upcoming/$', 'webcast_list', {'slug': 'upcoming'}, name='upcoming'),
    url(r'^mine/$', 'upcoming', name='upcoming_mine'),
    )
