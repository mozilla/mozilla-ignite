from challenges.models import SubmissionParent


def get_category_data(obj):
    return {
        'name': obj.name,
        'slug': obj.slug,
    }


def get_author(profile):
    user = profile.user
    return {
        'name': profile.name,
        'title': profile.title,
        'website': profile.website,
        'bio': profile.bio,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }


def get_phase_data(phase):
    return {
        'name': phase.name,
        'start_date': phase.start_date,
        'end_date': phase.end_date,
        'judging_start_date': phase.judging_start_date,
        'judging_end_date': phase.judging_end_date,
        'order': phase.order
    }


def get_phase_round_data(obj):
    return {
        'name': obj.name,
        'slug': obj.slug,
        'start_date': obj.start_date,
        'end_date': obj.end_date,
        'judging_start_date': obj.judging_start_date,
        'judging_end_date': obj.judging_end_date,
    }


def get_submission_data(obj):
    data = {
        'title': obj.title,
        'brief_description': obj.brief_description,
        'description': obj.description,
        'category': get_category_data(obj.category),
        'created_by': get_author(obj.created_by),
        'created_on': obj.created_on,
        'updated_on': obj.updated_on,
        'is_winner': obj.is_winner,
        'is_draft': obj.is_draft,
        'phase': get_phase_data(obj.phase),
        'collaborators': obj.collaborators,
        'life_improvements': obj.life_improvements,
        'take_advantage': obj.take_advantage,
        'interest_making': obj.interest_making,
        'team_members': obj.team_members,
        'repository_url': obj.repository_url,
        'blog_url': obj.blog_url,
        'required_effort': obj.required_effort,
    }
    if obj.sketh_note:
        data['sketh_note'] = obj.sketh_note.url
    if obj.phase_round:
        data['phase_round'] = get_phase_round_data(obj.phase_round)
    return data


def get_parent_data(parent):
    data = {
        'name': parent.name,
        'slug': parent.slug,
        'created': parent.created,
        'modified': parent.modified,
        'is_featured': parent.is_featured,
    }
    if parent.submission:
        submission_data = get_submission_data(parent.submission)
        data.update(submission_data)
    return data


def export_entries():
    """Export all the existing entries."""
    parent_list = (SubmissionParent.objects
                   .filter(status=SubmissionParent.ACTIVE))
    entries = []
    for parent in parent_list:
        entries.append(get_parent_data(parent))
    return entries
