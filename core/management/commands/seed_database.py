import random
import datetime
import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Sum

from ... import constants as cc
from ... import models as cm
from ...get_pic import get_image_urls


class DryRunError(Exception):
    pass


class Command(BaseCommand):
    help = "Run actions on a submission."

    def add_arguments(self, parser):
        pass
        # parser.add_argument('action')

        parser.add_argument('-g', '--group', type=str, default='EE')
        # parser.add_argument('-m', '--message', help='(optional) give a reason for the notes log')
        # # parser.add_argument('--no-bound', action='store_true', help='skip all bound submissions')
        # # parser.add_argument('--only-bound', action='store_true', help='skip all non-bound submissions')
        parser.add_argument('-n', '--dry-run', action='store_true', help='just print quotes you would regen')
        # # parser.add_argument('-o', '--output-csv-path', type=str, metavar='CSVPATH', help='write recalculation data to CSVPATH')
        # parser.add_argument('--change-by', type=int, help="User ID of person changing.")
        # parser.add_argument('--profile', default=None, help="If provided, write a profile output to the provided path.")

    def handle(self, *args, **options):
        self._handle(*args, **options)

    def _handle(self, *args, **options):
        # if not options['submission'] and not options['quote']:
        #     logging.disable(logging.CRITICAL)

        group = options['group']

        try:
            with transaction.atomic():
                _seed_database(cc.GROUPS[group])
                if options['dry_run']:
                    raise DryRunError('dry run')
        except DryRunError:
            print("Rolled back due to dry run...")


def _seed_database(group_data):
    print("Purging and reseeding bird database...")
    data = []
    for choice in group_data["choices"]:
        data += get_image_urls(species="", taxonCode=choice["taxonCode"], **group_data.get('media_filter_params', {}))

    random.shuffle(data)

    def parse_date(obsdttm):
        # 6 sep 2019
        return datetime.datetime.strptime(obsdttm, "%d %b %Y").date()

    with transaction.atomic():
        cm.Bird.objects.filter(group=group_data["code"]).delete()
        max_id = 0
        for bird_data in data:
            max_id += 1
            cm.Bird.objects.create(
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
