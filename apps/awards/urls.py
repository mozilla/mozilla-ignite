from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'awards.views',
    url(r'^(?P<submission_id>\d+)/$', 'award', name='award')
    #url(r'', '', name='')
    )
