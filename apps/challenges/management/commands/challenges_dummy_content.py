from datetime import datetime
from dateutil.relativedelta import relativedelta
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User, Group

from challenges.models import (Submission, Category, Phase, Challenge, Project,
                               JudgingCriterion)
from challenges.management.commands.dummy_utils import (create_submissions,
                                                        get_random_winners,
                                                        _random_words,
                                                        create_user)
from timeslot.models import TimeSlot, Release


# Expected constants in the DB
IGNITE_PROJECT_SLUG = 'us-ignite'
IGNITE_CHALLENGE_SLUG = 'ignite-challenge'
IGNITE_IDEATION_NAME = 'Ideation'
IGNITE_DEVELOPMENT_NAME = 'Development'


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

   Open the development Phase adding new submissions and winners

   python manage.py challenges_dummy_content --development --submissions --winners

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
        make_option('--submissions',
                    action='store_true',
                    default=False,
                    dest='submissions',
                    help='Adds submissions for the all the open Phase/Round'),
        make_option('--winners',
                    action='store_true',
                        default=False,
                    dest='winners',
                    help='Adds random winning submissions for the closed Phases'),
        make_option('--judging',
                    action='store_true',
                    default=False,
                    dest='judging',
                    help='Opens the judging stage in closed Phases'),
        make_option('--webcast',
                    action='store_true',
                    default=False,
                    dest='webcast',
                    help='Creates and releases tickets for the webcast'),
        )

    def _update_object(self, phase, **kwargs):
        """Update the ``Phase`` with the provides_values"""
        for attr, value in kwargs.items():
            setattr(phase, attr, value)
        phase.save()
        return phase

    def _update_rounds(self, development, with_open_rounds=True, judging=False):
        """Creates or manages ``PhaseRounds`` for the given ``Phase``
        if ``with_open_rounds`` is disabled all the rounds will be closed
        """
        rounds = development.phaseround_set.all()
        if not rounds:
            # Create 3 dummy phases if there is none available
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
        answer = raw_input('This will IRREVERSIBLY add TEST DATA to your '
                           'database. Proceed (yes/no)? ')
        if answer != 'yes':
            raise CommandError('Phew. Import canceled.')

        # Any super user is a judge
        judging_group = Group.objects.get(name='Judges')
        for user in User.objects.filter(is_superuser=True):
            judging_group.user_set.add(user)

        if options['judging']:
            print "Creating Judges"
            for i in range(10):
                judge = create_user(_random_words(1))
                judging_group.user_set.add(judge.user)
            criteria = JudgingCriterion.objects.all()
            if not criteria:
                print "Creating judging criteria"
                questions = ['Awesomeness', 'Inovation', 'Feasibility']
                criteria_list = [JudgingCriterion.objects.create(question=q) \
                                 for q in questions]

        ideation = Phase.objects.get_ideation_phase()
        if not ideation:
            raise CommandError('You need an Ideation Phase')
        development = Phase.objects.get_development_phase()
        if not development:
            # We need a development phase
            print "Creating a Development phase"
            challenge = Challenge.objects.get(slug=IGNITE_CHALLENGE_SLUG)
            development = Phase.objects.create(name=IGNITE_DEVELOPMENT_NAME,
                                               challenge=challenge, order=2)
        category = Category.objects.all()[0]
        now = datetime.utcnow()
        delta = relativedelta(days=15)
        # Ideation ``Phase``
        if options['ideation']:
            print "Opening Ideation Phase"
            start_date = now - delta
            end_date = now + delta
            judging_start_date = end_date
            judging_end_date = end_date
        else:
            print "Closing Ideation Phase"
            start_date = now - delta - delta
            end_date = now - delta
            judging_start_date = end_date
            if options['judging']:
                print "Opening judging on Ideation"
                judging_end_date = end_date + delta + delta
            else:
                judging_end_date = end_date
        ideation = self._update_object(ideation, start_date=start_date,
                                       end_date=end_date,
                                       judging_start_date=judging_start_date,
                                       judging_end_date=judging_end_date)
        if options['judging']:
            print "Adding judging criteria to Ideation"
            for criterion in criteria_list:
                ideation.phasecriterion_set.create(criterion=criterion)
        if options['submissions']:
            print "Adding submissions for the Ideation Phase"
            create_submissions(ideation, category, with_parents=True)
        if options['winners']:
            print "Setting up winners for the Ideation Phase"
            get_random_winners(ideation)
        # Development ``Phase``
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
        if options['submissions']:
            print "Adding submissions for the Development Phase"
            create_submissions(development, category, phase_round=rounds[0],
                               with_parents=True)
        if options['winners']:
            print "Setting up winners for the Development Phase"
            get_random_winners(development, phase_round=rounds[0])

        if options['webcast']:
            try:
                release = Release.objects.get(phase=ideation)
            except Release.DoesNotExist:
                print "Creating a Release for the timeslots"
                release = Release.objects.create(name='Release Ideation',
                                                 phase=ideation,
                                                 is_current=True)
            timeslot_date = now + relativedelta(days=15)
            print "Creating Timeslots for the release"
            for i in range(10):
                TimeSlot.objects.create(start_date=timeslot_date,
                                        end_date=timeslot_date,
                                        release=release)
        print "Done!"
