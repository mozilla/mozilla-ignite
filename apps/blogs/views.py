from Blogs.tasks import update_site_feeds
from django.http import HttpResponseRedirect

def test_blog_importer(request):
    update_site_feeds()

    return HttpResponseRedirect('/admin/blogs/blogentry/')
