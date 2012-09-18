import jingo

from django.http import Http404

from resources.models import Resource


def object_list(request, template='resources/object_list.html'):
    """Lists the current resources"""
    resource_list = Resource.objects.filter(status=Resource.PUBLISHED)
    context = {
        'object_list': resource_list,
        }
    return jingo.render(request, template, context)


def resource_page(request, slug, template='resources/pages/base.html'):
    """ Grab the intended resource from the DB so we can render it """
    resource_page = Resource.objects.get(slug=slug)
    if not resource_page:
        raise Http404
    context = {
        'page_data': resource_page
    }
    template = 'resources/pages/%s' % resource_page.template
    return jingo.render(request, template, context)
