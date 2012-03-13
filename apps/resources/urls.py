from django.conf.urls.defaults import patterns,  url


urlpatterns = patterns(
    'resources.views',
    url(r'^$', 'object_list', name='object_list'),
    )
