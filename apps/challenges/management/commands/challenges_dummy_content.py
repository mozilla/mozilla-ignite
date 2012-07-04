from datetime import datetime
from dateutil.relativedelta import relativedelta
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from challenges.models import Submission, Category, Phase, Challenge, Project


class Command(BaseCommand):
    help = """Generates dummy fixtures for the ``Phases`` and ``RoundPhases``
    It requires at least ideation and development ``Phases`` created.
    Rounds in the development ``Phase`` will be created if missing

    Open the Ideation ``Phase``::

        python manage.py challenges_dummy_content --ideation

    Open the Development ``Phase`` (with an open round)::

        python manage.py challenges_dummy_content --development

    Open both the Ideation and Development ``Phases`` (with an open round)::

        python manage.py challenges_dummy_content --ideation --development

    Open the Development ``Phase`` (with the rounds closed)::

        python manage.py challenges_dummy_content --development --closedrounds

    """

    option_list = BaseCommand.option_list + (
        make_option('--ideation',
                    action='store_true',
                    dest='ideation',
                    help='Set the Ideation Phase Open'),
        make_option('--development',
                    action='store_true',
                    dest='development',
                    help='Set the Development Phase Open'),
        # Development Rounds are open by default
        make_option('--closedrounds',
                    action='store_true',
                    default=False,
                    dest='closed_rounds',
                    help='Set the Development Phase Rounds Closed'),
        )

    now = datetime.utcnow()

    def _update_object(self, phase, **kwargs):
        """Update the ``Phase`` with the provides_values"""
        for attr, value in kwargs.items():
            setattr(phase, attr, value)
        phase.save()
        return phase

    def _update_rounds(self, development, with_open_rounds=True):
        """Creates or manages ``PhaseRounds`` for the given ``Phase``
        if ``with_open_rounds`` is disabled all the rounds will be closed
        """
        rounds = development.phaseround_set.all()
        if not rounds:
            # Create 3 dummy phaess if there is none available
            print "Creating dummy Development Rounds"
            create_round = lambda i: (development.phaseround_set
                                      .create(name='Round %s' % i,
                                              start_date=development.end_date,
                                              end_date=development.end_date))
            rounds = [create_round(i) for i in range(1, 4)]
        print "Updating Development Rounds"
        # list the available rounds and open the first one.
        for i, item in enumerate(rounds):
            if i == 1 and with_open_rounds:
                print "Opening first Development Round"
                item.start_date = development.start_date
                item.end_date = development.end_date - relativedelta(days=1)
            else:
                item.start_date = development.end_date
                item.end_date = development.end_date
            item.save()
        return rounds

    def handle(self, *args, **options):
        # answer = raw_input('This will IRREVERSIBLY add TEST DATA to your '
        #                    'database. Proceed (yes/no)? ')
        # if answer != 'yes':
        #     raise CommandError('Phew. Import canceled.')
        ideation = Phase.objects.get_ideation_phase()
        development = Phase.objects.get_development_phase()
        now = datetime.utcnow()
        delta = relativedelta(days=15)
        # Ideation ``Phase``
        if ideation:
            if options['ideation']:
                print "Opening Ideation Phase"
                start_date = now - delta
                end_date = now + delta
            else:
                print "Closing Ideation Phase"
                start_date = now - delta - delta
                end_date = now - delta
            ideation = self._update_object(ideation, start_date=start_date,
                                           end_date=end_date)
        # Development ``Phase``
        if development:
            if options['development']:
                print "Opening Development Phase"
                start_date = now - relativedelta(days=3)
                end_date = now + delta + delta
            else:
                print "Closing Development Phase"
                start_date = now - delta - relativedelta(days=3)
                end_date = now - relativedelta(days=3)
            development = self._update_object(development,
                                              start_date=start_date,
                                              end_date=end_date)
        # create ``PhaseRounds`` for the development phase
        with_open_rounds = not options['closed_rounds']
        rounds = self._update_rounds(development, with_open_rounds)
        print "Done!"
