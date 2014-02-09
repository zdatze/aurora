import os
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from Challenge.models import Challenge
from Course.models import Course
from Elaboration.models import Elaboration
from PortfolioUser.models import PortfolioUser
from Stack.models import Stack, StackChallengeRelation
from Evaluation.models import Evaluation
from FileUpload.models import UploadFile


@login_required()
def stack(request):
    data = create_context_stack(request)
    return render_to_response('stack.html', data, context_instance=RequestContext(request))


@login_required()
def stack_page(request):
    data = create_context_stack(request)
    return render_to_response('stack_page.html', data, context_instance=RequestContext(request))


def create_context_stack(request):
    data = {}
    if 'id' in request.GET:
        user = RequestContext(request)['user']
        stack = Stack.objects.get(pk=request.GET.get('id'))
        data['stack_blocked'] = stack.is_blocked(user)
        stack_challenges = StackChallengeRelation.objects.all().filter(stack=stack)
        challenges_active = []
        challenges_inactive = []
        for stack_challenge in stack_challenges:
            print("-" * 200)
            print(stack_challenge.challenge.title)
            if stack_challenge.challenge.is_enabled_for_user(user):
                print("IS ENABLED")
                reviews = []
                for review in stack_challenge.challenge.get_reviews_written_by_user(user):
                    reviews.append({
                        'review': review,
                        'submitted': review.submission_time is not None
                    })
                for i in range(Challenge.reviews_per_challenge - len(reviews)):
                    reviews.append({})
                challenge_active = {
                    'challenge': stack_challenge.challenge,
                    'submitted': stack_challenge.challenge.submitted_by_user(user),
                    'reviews': reviews,
                    'status': stack_challenge.challenge.get_status_text(user)
                }
                elaboration = Elaboration.objects.filter(challenge=stack_challenge, user=user)
                if elaboration:
                    elaboration = elaboration[0]
                    challenge_active['success'] = len(elaboration.get_success_reviews())
                    challenge_active['nothing'] = len(elaboration.get_nothing_reviews())
                    challenge_active['fail'] = len(elaboration.get_fail_reviews())
                    challenge_active['awesome'] = len(elaboration.get_awesome_reviews())
                    evaluation = elaboration.get_evaluation()
                    if evaluation:
                        challenge_active['points'] = evaluation.evaluation_points
                challenges_active.append(challenge_active)
            else:
                print("IS NOT ENABLED")
                challenges_inactive.append(stack_challenge.challenge)
        data['challenges_active'] = challenges_active
        data['challenges_inactive'] = challenges_inactive
    return data


@login_required()
def challenges_page(request):
    data = {}
    user = RequestContext(request)['user']
    course = RequestContext(request)['last_selected_course']
    course_stacks = Stack.objects.all().filter(course=course)
    data['course_stacks'] = []
    for stack in course_stacks:
        data['course_stacks'].append({
            'stack': stack,
            'status': stack.get_status_text(user),
            'points': stack.get_points(user)
        })
    return render_to_response('challenges_page.html', data, context_instance=RequestContext(request))


def create_context_challenge(request):
    data = {}
    if 'id' in request.GET:
        challenge = Challenge.objects.get(pk=request.GET.get('id'))
        user = RequestContext(request)['user']
        data['challenge'] = challenge
        if Elaboration.objects.filter(challenge=challenge, user=user).exists():
            elaboration = Elaboration.objects.get(challenge=challenge, user=user)
            data['elaboration'] = elaboration
            data['success'] = elaboration.get_success_reviews()
            data['nothing'] = elaboration.get_nothing_reviews()
            data['fail'] = elaboration.get_fail_reviews()
            if Evaluation.objects.filter(submission=elaboration).exists():
                data['evaluation'] = Evaluation.objects.filter(submission=elaboration)[0]
    return data


@login_required()
def challenge(request):
    data = create_context_challenge(request)
    return render_to_response('challenge.html', data, context_instance=RequestContext(request))


@login_required()
def challenge_page(request):
    data = create_context_challenge(request)
    return render_to_response('challenge_page.html', data, context_instance=RequestContext(request))