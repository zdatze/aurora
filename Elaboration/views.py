from django.contrib.auth.tests import *
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from Challenge.models import Challenge
from Elaboration.models import Elaboration
from PortfolioUser.models import PortfolioUser


@login_required()
def challenges(request):
    return render_to_response('elaboration.html', {}, context_instance=RequestContext(request))


@csrf_exempt
def save_elaboration(request):

    challenge_id = request.POST['challenge_id']
    elaboration_text = request.POST['elaboration_text']
    challenge = Challenge.objects.get(id=challenge_id)
    user = PortfolioUser.objects.get(id=request.user.id)

    # check if elaboration exists
    if Elaboration.objects.filter(challenge=challenge, user=user).exists():
        elaboration = Elaboration.objects.all().filter(challenge=challenge, user=user).order_by('id').latest('creationDate')
        elaboration.elaboration_text = ''
        elaboration.elaboration_text = elaboration_text
        elaboration.save()
    else:
        elaboration = Elaboration.objects.create(challenge=challenge, user= user, elaboration_text=elaboration_text)

    return HttpResponse()

