from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'timeslot.views',
    url(r'^(?P<entry_id>\d+)/$', 'object_list', name='object_list'),
    url(r'^(?P<entry_id>\d+)/(?P<object_id>[\w]+)/$', 'object_detail',
        name='object_detail'),
    )
