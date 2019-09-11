import datetime
import random
import collections

from django.core.cache import cache
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.db import IntegrityError, transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect

from lazysignup.decorators import allow_lazy_user

from . import models as cm
from . import constants as cc


def get_image(group, last_index):
    next_bird = (
        cm.Bird.objects.filter(
            group=group, seq__gt=last_index if last_index else 0, is_active=True
        )
        .order_by("seq")
        .first()
    )
    if next_bird:
        return next_bird

    raise RuntimeError("no more birds.")


@allow_lazy_user
def index(request):
    # if request.user.is_anonymous:
    #     try:
    #         user = cm.User.objects.create_superuser(
    #             username="Scott", email="scott.stafford@gmail.com", password=""
    #         )
    #     except IntegrityError:
    #         user = cm.User.objects.get(username="Scott")
    #     from django.contrib.auth import login
    #     from django.conf import settings

    #     login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
    # else:
    #     user = request.user

    template = loader.get_template("core/index.html")

    context = {"groups": cc.GROUPS}

    return HttpResponse(template.render(context, request))


@allow_lazy_user
def account(request):
    if request.user.is_anonymous:
        return redirect("/")

    template = loader.get_template("core/account.html")

    # stats = get_bird_stats(bird_to_guess, request.user)
    context = {"user_stats": get_user_stats(request.user)}

    return HttpResponse(template.render(context, request))


def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return redirect("/")


@allow_lazy_user
def identify(request, group_code, bird_seq=None):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # _seed_database(groups['EE'])

    user = request.user
    assert user is not None

    template = loader.get_template("core/identify.html")

    last_seq = (
        cm.Bird.objects.filter(group=group_code, guess__user=user)
        .order_by("-seq")
        .values_list("seq", flat=True)
        .first()
    )
    if bird_seq is None:
        bird_seq = (last_seq if last_seq else 0) + 1
    bird_to_guess = get_image(group_code, bird_seq)
    # served_birds[bird_to_guess['assetId']] = bird_to_guess
    bird_stats = get_bird_stats(bird_to_guess)
    user_stats = get_user_stats(request.user)

    context = {
        # 'bird': bird_to_guess,
        "bird_id": bird_to_guess.id,
        "image_url": bird_to_guess.image_url,
        "location": bird_to_guess.location_line1
        + " in "
        + bird_to_guess.location_line2,
        "observation_date": bird_to_guess.observation_date.isoformat(),
        "photo_by": bird_to_guess.ebird_user_display_name,
        "group": cc.GROUPS[group_code],
        "confidences": cc.CONFIDENCES,
        "bird_stats": bird_stats,
        "user_stats": user_stats,
    }

    # import pprint

    # pprint.pprint(bird_to_guess.__dict__)
    # pprint.pprint(bird_stats)
    # pprint.pprint(user_stats)

    return HttpResponse(template.render(context, request))


def get_user_stats(user):
    my_guesses = cm.Guess.objects.filter(user=user)

    my_correct_guesses = my_guesses.filter(is_correct=True).count()

    score = 0
    for g in my_guesses:
        if g.is_correct:
            score += g.confidence
        else:
            score -= g.confidence

    # my_score = my_guesses.filter(is_correct=True).count()

    ret = {
        "my_count": my_guesses.count(),
        "my_correct_guesses": my_correct_guesses,
        "my_score": score,
    }
    print("stats")
    print(ret)
    return ret


def get_bird_stats(bird):
    guessed_species = collections.defaultdict(int)
    for g in cm.Guess.objects.filter(bird=bird):
        guessed_species[g.species_code] += 1

    count = cm.Guess.objects.filter(bird=bird).count()

    ret = {"bird_count": count, "guessed_species": guessed_species}
    print("stats")
    print(ret)
    return ret


@csrf_exempt
def api_guess(request):
    bird_id = request.POST.get("bird_id")
    guess = request.POST.get("guess")
    confidence = request.POST.get("confidence")

    b = cm.Bird.objects.get(id=bird_id)

    # try:
    #     correct_choice = served_birds[bird_id]
    # except:
    #     raise RuntimeError("bad bird id")

    is_correct = b.species_code == guess
    cm.Guess.objects.create(
        bird=b,
        user=request.user,
        species_code=guess,
        confidence=confidence,
        is_correct=is_correct,
    )

    return JsonResponse(
        {
            "is_correct": is_correct,
            "correct_answer": b.species_code,
            "ebird_checklist_url": f"https://ebird.org/view/checklist/{b.ebird_checklist_id}",
            "bird_stats": get_bird_stats(b),
            "user_stats": get_user_stats(request.user),
        }
    )


@csrf_exempt
def api_deactivate(request):
    bird_id = request.POST.get("bird_id")

    b = cm.Bird.objects.get(id=bird_id)
    b.is_active = False
    b.deactivated_on = timezone.now()
    b.deactivated_by = request.user
    b.save()

    return JsonResponse({})

