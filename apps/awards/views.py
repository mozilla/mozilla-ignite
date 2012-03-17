from awards.forms import AwardForm
from awards.models import JudgeAllowance
from challenges.decorators import judge_required
from challenges.models import Submission
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.views.decorators.http import require_POST
from tower import ugettext as _

@judge_required
@require_POST
def award(request, submission_id, project=None, slug=None):
    """Awards an ammount to a gren-lit ``Submission`` by a Judge"""
    try:
        submission = (Submission.objects
                      .select_related('phase')
                      .get(id=submission_id, phase__challenge__slug=slug,
                           phase__challenge__project__slug=project,
                           is_winner=True, is_draft=False))
    except Submission.DoesNotExist:
        raise Http404
    judge_data = {
        'judge': request.user.get_profile(),
        'phase': submission.phase,
        }
    if submission.phase.current_round:
        judge_data.update({'phase_round': submission.phase_current_round})
    try:
        judge_allowance = JudgeAllowance.objects.get(**judge_data)
    except JudgeAllowance.DoesNotExist:
        raise Http404
    form = AwardForm(request.POST)
    if form.is_valid():
        is_allocated = judge_allowance.allocate(form.cleaned_data['amount'],
                                                submission)
        if is_allocated:
            message = _("You've successfuly awarded this Enry")
            messages.success(request, message)
            return HttpResponseRedirect(submission.get_absolute_url())
    message = _("You don't have enough funding for award this submission")
    messages.error(request, message)
    return HttpResponseRedirect(submission.get_absolute_url())
