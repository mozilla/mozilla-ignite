from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^(?P<project>[\w-]+)/participation/(?P<slug>[\w-]+)/$',
        'participation.views.show',
        name='participation_show'),
    url(r'^(?P<project>[\w-]+)/participation/(?P<slug>[\w-]+)/entries/add/$',
        'participation.views.create_entry',
        name='participation_create')
)
