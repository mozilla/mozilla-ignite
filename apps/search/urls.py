from django.conf.urls.defaults import patterns, url
from search.views import CustomSearchView

urlpatterns = patterns(
    '',
    url(r'^$', CustomSearchView(), name='search'),
    )
