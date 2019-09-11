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

from .get_pic import get_image_urls

from . import models as cm


# global image_urls
# image_urls = {}


# served_birds = {}


# def get_image(birdname):
#     global image_urls

#     try:
#         bird_urls = image_urls[birdname]
#     except KeyError:
#         bird_urls = image_urls[birdname] = get_image_urls(species="", taxonCode=birdname)

#     try:
#         return bird_urls.pop()
#     except ValueError:
#         bird_urls = image_urls[birdname] = get_image_urls(species="", taxonCode=birdname)
#         return bird_urls.pop()


def _seed_database(group_data):
    print("Purging and reseeding bird database...")
    cm.Bird.objects.filter(group=group_data["code"]).delete()

    data = []
    for choice in group_data["choices"]:
        data += get_image_urls(species="", taxonCode=choice["taxonCode"])

    random.shuffle(data)

    def parse_date(obsdttm):
        # 6 sep 2019
        return datetime.datetime.strptime(obsdttm, "%d %b %Y").date()

    max_id = 0
    for bird_data in data:
        max_id += 1
        new_bird = cm.Bird.objects.create(
            asset_id=bird_data["assetId"],
            # ebird_image_data=bird_data,
            group=group_data["code"],
            species_code=bird_data["speciesCode"],
            seq=max_id,
            common_name=bird_data["commonName"],
            image_url=bird_data["largeUrl"],
            location_line1=bird_data["locationLine1"],
            location_line2=bird_data["locationLine2"],
            observation_date=parse_date(bird_data["obsDttm"]),  # "22 Jun 2019",
            ebird_user_id=bird_data["userId"],
            ebird_rating=bird_data["rating"],
            ebird_user_display_name=bird_data["userDisplayName"],
            ebird_checklist_id=bird_data["eBirdChecklistId"],
            image_width=bird_data["width"],
            image_height=bird_data["height"],
            is_active=True,
        )


groups = {
    "EE": {
        "code": "EE",
        "name": "Eastern Empids",
        "choices": [
            {"name": "Alder Flycatcher", "taxonCode": "aldfly"},
            {"name": "Willow Flycatcher", "taxonCode": "wilfly"},
            {"name": "Least Flycatcher", "taxonCode": "leafly"},
            {"name": "Yellow-bellied Flycatcher", "taxonCode": "yebfly"},
            {"name": "Acadian Flycatcher", "taxonCode": "acafly"},
            {"name": "Eastern Wood-Pewee", "taxonCode": "eawpew"},
            # {'name': "Eastern Phoebe", "taxonCode": ""},
        ],
    }
}
confidences = [
    {"name": "Low", "abbrev": "L", "value": 1},
    {"name": "Medium", "abbrev": "M", "value": 5},
    {"name": "High", "abbrev": "H", "value": 10},
]


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
    # # populate some more...
    # first_new_bird = None
    # data = get_image_urls(species="", taxonCode=species_code)
    # max_id = cm.Bird.objects.filter(species_code=species_code).count()
    # for bird_data in data:
    #     max_id += 1

    #     if not first_new_bird:
    #         first_new_bird = new_bird

    # return first_new_bird


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

    context = {"groups": groups}

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
    # last_seq = cm.Guess.objects.filter(user=user).order_by('-bird__species_seq').values_list('bird__species_seq', flat=True).first()
    if bird_seq is None:
        bird_seq = last_seq + 1
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
        "group": groups[group_code],
        "confidences": confidences,
        "bird_stats": bird_stats,
        "user_stats": user_stats,
    }

    import pprint

    pprint.pprint(bird_to_guess.__dict__)
    pprint.pprint(bird_stats)
    pprint.pprint(user_stats)

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

