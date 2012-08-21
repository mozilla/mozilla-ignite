from challenges.models import SubmissionParent
from haystack import indexes

class SubmissionParentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    user = indexes.CharField(model_attr='submission__created_by__name')
    category = indexes.CharField(model_attr='submission__category__name',
                                 faceted=True)

    def get_model(self):
        return SubmissionParent
