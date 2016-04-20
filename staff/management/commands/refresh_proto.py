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


from pprint import PrettyPrinter

from django.core.management.base import BaseCommand
from django.db.utils import DatabaseError

from patron.models import Format, Language, PickupLocation
from sierra.models import LanguagePropertyMyuser, LocationMyuser, MaterialPropertyMyuser


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pp = PrettyPrinter()

    def handle(self, *args, **options):
        self._refresh_formats()
        self._refresh_languages()
        self._refresh_pickup_locations()

    def _refresh_formats(self):
        recs_in_autoholds = {x.code: x for x in Format.objects.all()}
        recs_in_sierra = {x.code: x for x in MaterialPropertyMyuser.objects.using('sierra').filter(is_public=True)}
        added_formats, removed_formats = self._diff(recs_in_autoholds, recs_in_sierra)
        removed_count = 0
        for x in removed_formats:
            try:
                x.delete()
                removed_count += 1
                self.stdout.write('Removed format {}'.format(x))
            except DatabaseError as e:
                self.stdout.write(
                    'Failed to remove format {}: {}'.format(x, e),
                    style_func=self.style.WARNING
                )
        added_count = 0
        for x in added_formats:
            try:
                f = Format(
                        code=x.code,
                        value=x.name,
                        active=True
                )
                f.save()
                added_count += 1
                self.stdout.write('Added format {}'.format(f))
            except DatabaseError as e:
                self.stdout.write(
                    'Failed to add format {}: {}'.format(x, e),
                    style_func=self.style.WARNING
                )
        if removed_count > 0 or added_count > 0:
            self.stdout.write(
                'Added {} and removed {} formats'.format(added_count, removed_count),
                style_func=self.style.SUCCESS
            )

    def _refresh_languages(self):
        recs_in_autoholds = {x.code: x for x in Language.objects.all()}
        recs_in_sierra = {x.code: x for x in LanguagePropertyMyuser.objects.using('sierra').filter(is_public=True)}
        added_languages, removed_language = self._diff(recs_in_autoholds, recs_in_sierra)
        removed_count = 0
        for x in removed_language:
            try:
                x.delete()
                removed_count += 1
                self.stdout.write('Removed language {}'.format(x))
            except DatabaseError as e:
                self.stdout.write(
                    'Failed to remove language {}: {}'.format(x, e),
                    style_func=self.style.WARNING
                )
        added_count = 0
        for x in added_languages:
            try:
                l = Language(
                    code=x.code,
                    name=x.name,
                    active=True
                )
                l.save()
                added_count += 1
                self.stdout.write('Added language {}'.format(l))
            except DatabaseError as e:
                self.stdout.write(
                    'Failed to add language {}: {}'.format(x, e),
                    style_func=self.style.WARNING
                )
        if removed_count > 0 or added_count > 0:
            self.stdout.write(
                'Added {} and removed {} languages'.format(added_count, removed_count),
                style_func=self.style.SUCCESS
            )

    def _refresh_pickup_locations(self):
        recs_in_autoholds = {x.code: x for x in PickupLocation.objects.all()}
        recs_in_sierra = {x.code: x for x in LocationMyuser.objects.using('sierra').filter(is_public=True)}
        added_pickup_locations, removed_pickup_locations = self._diff(recs_in_autoholds, recs_in_sierra)
        removed_count = 0
        for x in removed_pickup_locations:
            try:
                x.delete()
                removed_count += 1
                self.stdout.write('Removed pickup location {}'.format(x))
            except DatabaseError as e:
                self.stdout.write(
                        'Failed to remove pickup location {}: {}'.format(x, e),
                        style_func=self.style.WARNING
                )
        added_count = 0
        for x in added_pickup_locations:
            try:
                pl = PickupLocation(
                        code=x.code,
                        name=x.name,
                        active=True
                )
                pl.save()
                added_count += 1
                self.stdout.write('Added pickup location {}'.format(pl))
            except DatabaseError as e:
                self.stdout.write(
                    'Failed to add pickup location {}: {}'.format(x, e),
                    style_func=self.style.WARNING
                )
        if removed_count > 0 or added_count > 0:
            self.stdout.write(
                'Added {} and removed {} pickup locations'.format(added_count, removed_count),
                style_func=self.style.SUCCESS
            )

    def _diff(self, recs_in_autoholds, recs_in_sierra):
        codes_in_autoholds = set(recs_in_autoholds)
        codes_in_sierra = set(recs_in_sierra)
        added_codes = codes_in_sierra - codes_in_autoholds
        removed_codes = codes_in_autoholds - codes_in_sierra
        added = [recs_in_sierra[x] for x in added_codes]
        removed = [recs_in_autoholds[x] for x in removed_codes]
        return added, removed
