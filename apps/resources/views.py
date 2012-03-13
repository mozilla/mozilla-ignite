import jingo

from resources.models import Resource

def object_list(request, template='resources/object_list.html'):
    """Lists the current resources"""
    resource_list = Resource.objects.filter(status=Resource.PUBLISHED)
    context = {
        'object_list': resource_list,
        }
    return jingo.render(request, template, context)
