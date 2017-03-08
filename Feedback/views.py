import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template import RequestContext
from Course.models import Course
from .models import Lane, Issue
from django.http import HttpResponseBadRequest, HttpResponseNotFound, \
    HttpResponseForbidden


@login_required
def index(request, course_short_title):
    """
    index renders a simple html page, adds the react frontend code and some
    initial data, so that users don't have to make additional request to see
    the issues.
    """

    # Pass some values directly as js variables, so that the client doesn't
    # has to make additional requests.
    course = Course.get_or_raise_404(course_short_title)

    lanes = None
    if request.user.is_staff:
        lanes = Lane.objects.all().order_by('order')
    else:
        # Only staff is allowed to see hidden lanes.
        lanes = Lane.objects.filter(hidden=False).order_by('order')

    lanes = list(map(lambda lane: {
        'id': lane.pk, 'name': lane.name, 'issues': []}, lanes))

    # Issues are course specific.
    issues = Issue.objects.filter(course=course)

    issue_data = []
    for issue in issues:
        # Filter out any security issues, if the current user is not the owner
        # or an admin.
        if issue.type != 'security' or issue.author == request.user \
                or request.user.is_staff:
            issue_data.append(issue.serializable)

    data = {
        'lanes': lanes,
        'issues': issue_data,
        'current_user': {
            'is_staff': request.user.is_staff,
            'id': request.user.id,
        }
    }

    return render(
        request, 'Feedback/index.html',
        {
            'course': course,
            'data': json.dumps(data)
        }
    )


@login_required
def issue_display(request, course_short_title, issue_id):
    """
    Basically the same as the index, since react route will take care of
    showing the specific issue. Couldn't find out how to move all into the
    index function otherwise.
    """
    return index(request, course_short_title)


@login_required
def api_issue(request, course_short_title, issue_id):
    """
    API callback for getting editing or retrieving a certain issue.
    """
    issue = Issue.objects.get(pk=issue_id)

    # Currently not in use.
    if request.method == 'GET':
        # Only the staff and the author are able to see issues of the type
        # security.
        if issue.type != 'security' \
                or issue.author == request.user or request.user.is_staff:
            return JsonResponse(issue.serializable)
        else:
            return HttpResponseForbidden()
    elif request.method == 'PUT':
        # Edit a certain issue, is also used to switch the lane.

        # Only staff or the owner are allowed to edit issues.
        if issue.author != request.user and not request.user.is_staff:
            return HttpResponseForbidden()

        # Decoded the passed values.
        data = json.loads(request.body.decode('utf-8'))

        # Check if the user wants to switch the lane.
        if 'lane' in data and issue.lane.pk != data['lane']:
            # Only staff is allowed to change the issues lane.
            if not request.user.is_staff:
                return HttpResponseForbidden()
            new_lane = Lane.objects.get(pk=data['lane'])
            issue.lane = new_lane

        # Users can only edit the type, title or the body of an issue.
        if 'type' in data:
            issue.type = data['type']

        if 'title' in data:
            issue.title = data['title']

        if 'body' in data:
            issue.body = data['body']

        issue.save()

        # Return the issue, so redux/react can update the kanban immediately.
        return JsonResponse(issue.serializable)

    return JsonResponse([])


@login_required
def api_new_issue(request, course_short_title):
    """
    API callback to create a new issue.
    """
    if request.method == 'POST':
        course = Course.get_or_raise_404(course_short_title)
        lanes = Lane.objects.all().filter(hidden=False).order_by('order')

        data = json.loads(request.body.decode('utf-8'))
        user = RequestContext(request)['user']

        # You can't create an issue without a title, type or a body.
        if 'title' not in data or 'type' not in data or 'body' not in data:
            return HttpResponseForbidden()

        issue = Issue(
            author=user,
            course=course,
            lane=lanes[0],
            type=data['type'],
            title=data['title'],
            body=data['body'],
        )

        issue.save()
        return JsonResponse(issue.serializable)

    return JsonResponse([])


@login_required
def issue_comments(request, course_short_title, issue_id):
    """
    Special API callback that returns the html part of the comments for a
    certain issue.
    This is necessary, since the Feedback system reuses the Comments client
    side code.
    """
    issue = Issue.objects.get(pk=issue_id)
    # Only the staff and the author are able to see issues of the type
    # security.
    if issue.type == 'security' \
            and issue.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden()

    context = {
        'issue': issue,
        'course': Course.get_or_raise_404(course_short_title)
    }

    return render(request, "issue_comments.html", context)