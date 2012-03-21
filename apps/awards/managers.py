from django.db import models


class JudgeAllowanceManager(models.Manager):

    def get_for_judge(self, user_profile):
        """Gets the current ``Allowance`` for the Judge, from the ``RELEASED``
        ``Award``"""
        from awards.models import Award
        JudgeAllowance = self.model
        try:
            allowance = (JudgeAllowance.objects
                         .select_related('award', 'award__phase',
                                         'award__phase_round',)
                         .get(judge=user_profile,
                              award__status=Award.RELEASED))
        except JudgeAllowance.DoesNotExist:
            allowance = None
        return allowance
