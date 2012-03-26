import jingo

from django.http import Http404
from django.views.decorators.http import require_GET
from haystack.query import SearchQuerySet
from haystack.views import FacetedSearchView
from search.forms import CustomFacetedSearchForm

# @require_GET
# def search(request):
#     """Performs the search on the ``Submissions``"""
#     form = SearchForm(request.GET)
#     if not form.is_valid():
#         raise Http404
#     query = form.cleaned_data['q']
#     sqs = SearchQuerySet().auto_query(query)
#     context = {
#         'results': sqs,
#         'form': form,
#         }
#     return jingo.render(request, 'search/search.html', context)


class CustomSearchView(FacetedSearchView):
    """Uses jingo to render the pages"""

    def __init__(self, *args, **kwargs):
        # Needed to switch out the default form class.
        if kwargs.get('form_class') is None:
            kwargs['form_class'] = CustomFacetedSearchForm
        super(FacetedSearchView, self).__init__(*args, **kwargs)

    def create_response(self):
        """Generates the actual HttpResponse to send back to the user."""
        (paginator, page) = self.build_page()
        context = {
            'query': self.query,
            'form': self.form,
            'page': page,
            'paginator': paginator,
            'suggestion': None,
        }
        if self.results and hasattr(self.results, 'query') and self.results.query.backend.include_spelling:
            context['suggestion'] = self.form.get_suggestion()
        context.update(self.extra_context())
        return jingo.render(self.request, self.template, context)

    def extra_context(self):
        extra = super(CustomSearchView, self).extra_context()
        extra['days_remaining'] = self.request.phase['days_remaining']
        return extra
