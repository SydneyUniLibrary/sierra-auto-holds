# Copyright 2016 Susan Bennett, David Mitchell, Jim Nicholls
#
# This file is part of AutoHolds.
#
# AutoHolds is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# AutoHolds is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with AutoHolds.  If not, see <http://www.gnu.org/licenses/>.


from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import localtime, make_aware, now

from patron.models import Registration
from sierra.api import SierraApi_v2, SierraApiError


class Command(BaseCommand):

    help = 'Discover new bib records and place auto-holds on them'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sierra_api = None

    def handle(self, *args, **options):
        datetime_last_run = make_aware(datetime(2016, 3, 4))  # TODO: Track and retrieve last run date/time
        datetime_now = now()

        self.sierra_api = SierraApi_v2.login(
                settings.SIERRA_API.base_url,
                settings.SIERRA_API.client_key,
                settings.SIERRA_API.client_secret
        )

        new_bibs = self._get_new_bibs(datetime_last_run, datetime_now)
        # new_bibs = self._get_bibs(sierra_api, 1000001)
        self.stdout.write(
            'Found {} new bib records created between {} and {}'.format(
                len(new_bibs), localtime(datetime_last_run), localtime(datetime_now)
            )
        )
        for bib in new_bibs:
            try:
                self._process_bib(bib)
            except Exception as e:
                self.stdout.write(
                    'An error occurred while processing .b{}a: {}'.format(
                        bib.get('id', '?'), e
                    ),
                    style_func=self.style.ERROR
                )

    def _process_bib(self, bib):
        bib_rec_num = bib['id']
        if bib_rec_num == '4862252':
            raise Exception('Deliberate test of _process_bib going bang')
        bib_author = bib['author']
        if not bib_author:
            self.stdout.write(
                'Skipping .b{}a because it has no author'.format(bib_rec_num),
                style_func=self.style.NOTICE
            )
            return
        bib_material_type_code = bib['materialType']['code']
        bib_language_code = bib['lang']['code']
        regs = Registration.objects.filter(
            author__name__iexact=bib_author,
            format__code=bib_material_type_code,
            format__active=True,
            language__code=bib_language_code,
            language__active=True
        ).order_by('hold_queue_order')
        self.stdout.write(
            'Found {} registrations for .b{}a, format {} and language {}'.format(
                len(regs), bib_rec_num, bib_material_type_code, bib_language_code
            )
        )
        for reg in regs:
            try:
                self._place_hold(bib_rec_num, reg)
            except Exception as e:
                self.stdout.write(
                    'An error occurred while processing registration id {} for .b{}a: {}'.format(
                        reg.id, bib_rec_num, e
                    ),
                    style_func=self.style.ERROR
                )
        if len(regs) > 1:
            first_reg = regs[0]
            first_reg.move_to_last_in_hold_queue_order()
            self.stdout.write(
                'Moved .p{}a to bottom of queue for .b{}a, format {} and language {}. New position is {}'.format(
                    first_reg.patron.patron_record_number, bib_rec_num, bib_material_type_code,
                    bib_language_code, first_reg.hold_queue_order
                )
            )

    def _place_hold(self, bib_rec_num, registration):
        patron_rec_num = registration.patron.patron_record_number
        pickup_location = registration.patron.pickup_location.code
        try:
            self.sierra_api.patrons_place_hold(patron_rec_num, 'b', bib_rec_num, pickup_location)
            self.stdout.write(
                'Successfully placed hold on .b{}a for .p{}a with pickup at {} (registration id {})'.format(
                    bib_rec_num, patron_rec_num, pickup_location, registration.id
                ),
                style_func=self.style.SUCCESS
            )
        except SierraApiError as e:
            self.stdout.write(
                'Failed to place hold on .b{}a for .p{}a (registration id {}): {}'.format(
                    bib_rec_num, patron_rec_num, registration.id, e
                ),
                style_func=self.style.WARNING
            )

    def _get_bibs(self, *bib_ids):
        result = list()
        for bib_id in bib_ids:
            result.append(self.sierra_api.bibs_get_for_id(bib_id, fields='id,author,materialType,lang'))
        return result

    def _get_new_bibs(self, created_date_from, created_date_to):
        result = self.sierra_api.bibs_get(
            created_date={'range_from': created_date_from, 'range_to': created_date_to},
            fields='id,author,materialType,lang',
            deleted=False,
            suppressed=False
        )
        return result['entries']
