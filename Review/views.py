import json
from datetime import datetime

from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404

from Review.models import Review
from Elaboration.models import Elaboration
from Challenge.models import Challenge
from ReviewQuestion.models import ReviewQuestion
from ReviewAnswer.models import ReviewAnswer
from Notification.models import Notification


def create_context_review(request):
    data = {}
    if 'id' in request.GET:
        user = RequestContext(request)['user']
        challenge = Challenge.objects.get(pk=request.GET.get('id'))
        if not challenge.is_enabled_for_user(user):
            return Http404
        review = Review.get_open_review(challenge, user)
        if not review:
            if challenge.has_enough_user_reviews(user):
                return Http404
            review_candidate = Elaboration.get_review_candidate(challenge, user)
            if review_candidate:
                review = Review(elaboration=review_candidate, reviewer=user)
                review.save()
            else:
                return Http404
        data['review'] = review
        data['stack_id'] = challenge.get_stack().id
        review_questions = ReviewQuestion.objects.filter(challenge=challenge).order_by("order")
        data['questions'] = review_questions
    return data


@login_required()
def review(request):
    data = create_context_review(request)
    return render_to_response('review.html', data, context_instance=RequestContext(request))


@login_required()
def review_answer(request):
    user = RequestContext(request)['user']
    course = RequestContext(request)['last_selected_course']
    if request.POST:
        data = request.body.decode(encoding='UTF-8')
        data = json.loads(data)
        review_id = data['review_id']
        answers = data['answers']
        try:
            review = Review.objects.get(pk=review_id)
            challenge = review.elaboration.challenge
            if not challenge.is_enabled_for_user(user):
                raise Http404
            if not review == Review.get_open_review(challenge, user):
                raise Http404
        except:
            raise Http404
        review.appraisal = data['appraisal']

        for answer in answers:
            question_id = answer['question_id']
            text = answer['answer']
            review_question = ReviewQuestion.objects.get(pk=question_id)
            ReviewAnswer(review=review, review_question=review_question, text=text).save()
            # send notifications
        if review.appraisal == review.NOTHING:
            Notification(
                user=review.elaboration.user,
                course=course,
                text=Notification.BAD_REVIEW + review.elaboration.challenge.title,
                image_url=review.elaboration.challenge.image.url,
                link="/challenges/challenge?id=" + str(review.elaboration.challenge.id)
            ).save()
        else:
            final_challenge = review.elaboration.challenge.get_final_challenge()
            if final_challenge.is_enabled_for_user(review.elaboration.user):
                obj, created = Notification.objects.get_or_create(
                    user=review.elaboration.user,
                    course=course,
                    text=Notification.ENOUGH_PEER_REVIEWS + final_challenge.title,
                    image_url=final_challenge.image.url,
                    link="/challenges/stack?id=" + str(review.elaboration.challenge.get_stack().id)
                )
    review.submission_time = datetime.now()
    review.save()
    return HttpResponse()