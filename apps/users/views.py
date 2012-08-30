import json

from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext

from activity.models import Activity
from users.models import Profile, Link
from users.forms import ProfileForm, ProfileLinksForm
from challenges.models import Submission, JudgeAssignment
from timeslot.models import TimeSlot, Release
from settings import INSTALLED_APPS

import jingo

ACTIVITY_PAGE_SIZE = 20


@login_required
def dashboard(request, page=0):
    """Display first page of activities for a users dashboard."""
    start = int(page) * ACTIVITY_PAGE_SIZE
    end = start + ACTIVITY_PAGE_SIZE
    profile = request.user.get_profile()
    all_activities = Activity.objects.filter(
        entry__link__project__in=profile.projects_following.all()
    ).select_related('entry', 'entry__link', 'entry__link__project').order_by(
        '-published_on'
    )
    activities = all_activities[start:end]
    if request.is_ajax():
        if not all_activities:
            raise Http404
        return jingo.render(request, 'activity/ajax/activity.html', {
            'activities': activities,
            'show_meta': True
        })
    return jingo.render(request, 'users/dashboard.html', {
        'profile': profile,
        'activities': activities,
        'has_more': len(all_activities) > end,
        'next_page': int(page) + 1,
        'total': len(all_activities)
    })


def signout(request):
    """Sign the user out, destroying their session."""
    auth.logout(request)
    return HttpResponseRedirect(reverse('innovate_splash'))


def profile(request, username):
    """Display profile page for user specified by ``username``.
    This page also acts as a hub for all the user notifications
    """
    user = get_object_or_404(auth.models.User, username=username)
    profile = get_object_or_404(Profile, user=user)
    if 'challenges' in INSTALLED_APPS:
        if profile.user == user:
            submissions = Submission.objects.current().filter(created_by=profile)
        else:
            submissions = Submission.objects.visible().filter(created_by=profile)
    # Filter on submission phase
    ideation_submissions = submissions.filter(phase__name='Ideation')
    development_submissions = submissions.filter(phase__name='Development')
    # Show the all the submission related data when the user is the owner
    need_booking_list = []
    booked_list = []
    if profile.user == user:
        release = Release.objects.get_current()
        booked_list = (TimeSlot.objects.select_related('submission')
                       .filter(submission__created_by=profile,
                               is_booked=True, release=release))
        booked_ids = [i.submission.id for i in booked_list]
        if release:
            need_booking_list = (Submission.objects
                                 .green_lit(release.phase, release.phase_round)
                                 .select_related('created_by')
                                 .filter(~Q(id__in=booked_ids),
                                         created_by=profile))
    # User has assigned judging tasks
    webcast_list = []
    if request.user.is_authenticated() and request.user.is_judge:
        # Determining if a user is a judge is quite expensive query-wise,
        # so we use the JudgeAssignment model to list the judge
        # booked webcasts, past and present.
        ids = (JudgeAssignment.objects.filter(judge=request.user.get_profile()).
               values_list('submission__id', flat=True))
        webcast_list = (TimeSlot.objects.
                        select_related('submission').
                        filter(is_booked=True, submission__in=ids))
    return jingo.render(request, 'users/profile.html', {
        'profile': profile,
        'social_links': profile.link_set.all() or False,
        'projects': profile.project_set.all() or False,
        'ideation_submissions': ideation_submissions or False,
        'development_submissions': development_submissions or False,
        'booked_list': booked_list,
        'need_booking_list': need_booking_list,
        'webcast_list': webcast_list,
    })


@login_required
def links(request):
    if not request.is_ajax():
        raise Http404
    profile = request.user.get_profile()
    links = Link.objects.filter(profile=profile).order_by('id')
    return jingo.render(request, 'users/links.html', {
        'links': links
    })


@login_required
def delete_link(request, id):
    link = get_object_or_404(Link, pk=id)
    if request.user.get_profile() != link.profile:
        raise Http404
    if request.method == 'POST':
        link.delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponseRedirect(reverse('users_edit'))
    return jingo.render(request, 'users/profile_link_delete.html', {
        'link': link
    })


@login_required
def add_link(request):
    profile = request.user.get_profile()
    if request.method == 'POST':
        form = ProfileLinksForm(data=request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            link.profile = profile
            link.save()
            return HttpResponseRedirect(reverse('users_edit'))
        else:
            if request.is_ajax():
                return HttpResponse(json.dumps(form.errors), status=400)
            return jingo.render(request, 'users/profile_link_add.html', {
                'form': form
            })
    form = ProfileLinksForm()
    return jingo.render(request, 'users/profile_link_add.html', {
        'form': form
    })


@login_required
def edit(request):
    """Edit the currently logged in users profile."""
    profile = request.user.get_profile()
    if request.method == 'POST':
        form = ProfileForm(data=request.POST,
                           files=request.FILES,
                           instance=profile)
        if form.is_valid():
            
            success_message = ugettext(u"Thank you \u2013 your profile has "
                                       u"been updated.")
            
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            # if the link form is present we have a few more checks to do
            if 'link_url' in request.POST:
                # adding in a link non-JS
                links_form = ProfileLinksForm(data={
                    'url': request.POST['link_url'],
                    'name': request.POST['link_name']
                })
                if links_form.is_valid():
                    link = links_form.save(commit=False)
                    link.profile = profile
                    link.save()
                messages.success(request, success_message)
                # links only valid on betafarm so feels safe to do this...
                return HttpResponseRedirect(reverse('users_profile', kwargs={
                    'username': request.user.username
                }))
            else:
                messages.success(request, success_message)
                return HttpResponseRedirect('/')
    form = ProfileForm(instance=profile)
    links = profile.link_set.all()
    return jingo.render(request, 'users/edit.html', {
        'form': form,
        'links': links
    })


def all(request, page=1):
    """Display a paginated, searchable list of users."""
    # TODO - Implement support for search.
    profiles = Profile.objects.all().order_by('name')
    profiles = filter(lambda p: p.has_chosen_identifier, profiles)
    paginator = Paginator(profiles, 15)
    return jingo.render(request, 'users/all.html', {
        'paginator': paginator,
        'profiles': paginator.page(page),
        'page': 'all'
    })


def active(request, page=1):
    """Display a list of the most active users."""
    # TODO - We don't have anything with which to measure activity yet.
    profiles = Profile.objects.all().order_by('-user__last_login')
    profiles = filter(lambda p: p.has_chosen_identifier, profiles)
    paginator = Paginator(profiles, 15)
    return jingo.render(request, 'users/all.html', {
        'paginator': paginator,
        'profiles': paginator.page(page),
        'page': 'active'
    })


def recent(request, page=1):
    """Display a list of the most recent users."""
    profiles = Profile.objects.all().order_by('-user__date_joined')
    profiles = filter(lambda p: p.has_chosen_identifier, profiles)
    paginator = Paginator(profiles, 15)
    return jingo.render(request, 'users/all.html', {
        'paginator': paginator,
        'profiles': paginator.page(page),
        'page': 'recent'
    })
