from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'resources.views',
    url(r'^$', 'object_list', name='object_list'),
    url(r'^labs/(?P<slug>[\w-]+)/$', 'resource_page', name='resource_page'),
    )
