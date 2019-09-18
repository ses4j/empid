import datetime
import logging
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
from lazysignup.utils import is_lazy_user

from . import models as cm
from . import constants as cc

logger = logging.getLogger(__name__)


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

    last_seq = (
        cm.Bird.objects.filter(group=group_code, guess__user=user)
        .order_by("-seq")
        .values_list("seq", flat=True)
        .first()
    )
    if bird_seq is None:
        bird_seq = last_seq if last_seq else 0
    bird_to_guess = get_image(group_code, bird_seq)
    # served_birds[bird_to_guess['assetId']] = bird_to_guess
    bird_stats = get_bird_stats(bird_to_guess)
    user_stats = get_user_stats(request.user)


    context = {
        # 'bird': bird_to_guess,
        "bird_id": bird_to_guess.id,
        "seq": bird_to_guess.seq,
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

    if is_lazy_user(request.user) and bird_to_guess.seq > 10:
        context['prompt_user_to_create'] = True


    # import pprint

    # pprint.pprint(bird_to_guess.__dict__)
    # pprint.pprint(bird_stats)
    # pprint.pprint(user_stats)

    template = loader.get_template("core/identify.html")
    return HttpResponse(template.render(context, request))


def _score_guess(g):
    if g.is_correct:
        return g.confidence
    else:
        return -g.confidence

from django.utils.timezone import make_aware
@allow_lazy_user
def leaderboard(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # _seed_database(groups['EE'])

    user = request.user
    assert user is not None

    template = loader.get_template("core/leaderboard.html")

    gs = cm.Guess.objects.all()
    scores = collections.defaultdict(int)
    confidences = collections.defaultdict(int)
    total = collections.defaultdict(int)
    correct = collections.defaultdict(int)
    last_guess_on = {}

    for g in gs:
        scores[g.user_id] += _score_guess(g)
        confidences[g.user_id] += g.confidence
        total[g.user_id] += 1
        correct[g.user_id] += 1 if g.is_correct else 0
        last_guess_on[g.user_id] = max(g.created, last_guess_on.get(g.user_id, make_aware(datetime.datetime(2000, 1, 1))))

    leader_data = list(sorted(scores.items(), key=lambda x: -x[1])[:20])
    leader_users = cm.User.objects.filter(id__in=[_[0] for _ in leader_data])
    leader_users = {_.id: (_.username if not is_lazy_user(_) else f"Anonymous #{_.id}") for _ in leader_users}
    

    leaderboard = []
    for user_id, score in leader_data:
        leaderboard.append(
            {
                "score": score,
                "user_id": user_id,
                "username": leader_users[user_id],
                "total": total[user_id],
                "correct": correct[user_id],
                "avg_confidence": round(float(confidences[user_id]) / float(total[user_id]), 1),
                "last_guess_on": last_guess_on[user_id], #.isoformat(),
            }
        )

    print(leaderboard)
    context = {"leaderboard": leaderboard}
    return HttpResponse(template.render(context, request))


def get_user_stats(user):
    my_guesses = cm.Guess.objects.filter(user=user)

    my_correct_guesses = my_guesses.filter(is_correct=True).count()

    score = 0
    for g in my_guesses:
        score += _score_guess(g)

    ret = {
        "my_count": my_guesses.count(),
        "my_correct_guesses": my_correct_guesses,
        "my_score": score,
    }
    # print("stats")
    # print(ret)
    return ret


def get_bird_stats(bird):
    guessed_species = collections.defaultdict(int)
    for g in cm.Guess.objects.filter(bird=bird):
        guessed_species[g.species_code] += 1

    count = cm.Guess.objects.filter(bird=bird).count()

    ret = {"bird_count": count, "guessed_species": guessed_species}
    # print("stats")
    # print(ret)
    return ret


@csrf_exempt
def api_guess(request):
    bird_id = request.POST.get("bird_id")
    guess = request.POST.get("guess")
    confidence = request.POST.get("confidence")
    comments = request.POST.get("comments", "")

    b = cm.Bird.objects.get(id=bird_id)

    # try:
    #     correct_choice = served_birds[bird_id]
    # except:
    #     raise RuntimeError("bad bird id")

    is_correct = b.species_code == guess
    g = cm.Guess.objects.create(
        bird=b,
        user=request.user,
        species_code=guess,
        confidence=confidence,
        is_correct=is_correct,
        comments=comments,
    )

    logger.info(f"Added guess: {g}")

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


@csrf_exempt
def api_comment(request):
    bird_id = request.POST.get("bird_id")
    comments = request.POST.get("comments", "")

    g = cm.Guess.objects.get(bird_id=bird_id, user=request.user)
    g.comments = comments
    logger.info(f"Added comment: {g}")
    g.save()

    return JsonResponse({})

