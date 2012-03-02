from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'webcast.views',
    url(r'^upcoming/$', 'webcast_list', name='upcoming'),
    url(r'^mine/$', 'upcoming', name='upcoming_mine'),
    )
