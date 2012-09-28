import jingo

from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from jinja2.exceptions import TemplateNotFound

from resources.models import Resource


def object_list(request, template='resources/object_list.html'):
    """Lists the current resources"""
    labs = Resource.objects.filter(
            status=Resource.PUBLISHED,
            resource_type=2
        ).order_by('-created')
    links = Resource.objects.filter(
            status=Resource.PUBLISHED,
            resource_type=1
        ).order_by('title')
    context = {
        'labs': labs,
        'links': links
        }
    return jingo.render(request, template, context)


def resource_page(request, slug, template='resources/pages/base.html'):
    """ Grab the intended resource from the DB so we can render it """
    try:
        resource_page = Resource.objects.get(slug=slug)
    except ObjectDoesNotExist:
        raise Http404

    context = {
        'page_data': resource_page
    }

    template = 'resources/pages/%s' % resource_page.template

    try:
        return jingo.render(request, template, context)
    except TemplateNotFound:
        raise Http404
