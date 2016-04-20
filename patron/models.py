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


from django.conf import settings
from django.db import models
from django.db.models.expressions import RawSQL


class Author(models.Model):
    name = models.CharField(max_length=255, unique=True)
    friendly_name = models.CharField(max_length=255)
    note = models.TextField(null=True, blank=True)
    patrons = models.ManyToManyField('Patron', through='Registration')

    def __str__(self):
        return self.name


class Format(models.Model):
    code = models.CharField(max_length=1)
    value = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    @staticmethod
    def default():
        return Format.objects.filter(code=settings.PATRON_DEFAULT_FORMAT).first()

    def __str__(self):
        return self.value


class Language(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    @staticmethod
    def default():
        return Language.objects.filter(code=settings.PATRON_DEFAULT_LANGUAGE).first()

    def __str__(self):
        return self.code


class PickupLocation(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    @staticmethod
    def default():
        return PickupLocation.objects.filter(code=settings.PATRON_DEFAULT_PICKUP_LOCATION).first()

    def __str__(self):
        return self.code


class Patron(models.Model):
    patron_record_number = models.IntegerField(unique=True)
    pickup_location = models.ForeignKey(PickupLocation, models.PROTECT)
    default_format = models.ForeignKey(Format, models.PROTECT)
    default_language = models.ForeignKey(Language, models.PROTECT)
    note = models.TextField(null=True, blank=True)
    authors = models.ManyToManyField('Author', through='Registration')

    @staticmethod
    def for_sierra_patron(sierra_patron):
        patron_record_number = sierra_patron['id']
        patron = Patron.objects.filter(patron_record_number=patron_record_number).first()
        if not patron:
            home_library_code = sierra_patron['fixedFields']['53']['value'].strip()
            pickup_location = PickupLocation.objects.filter(code=home_library_code).first()
            if not pickup_location:
                pickup_location = PickupLocation.default()
            default_format = Format.default()
            pref_language_code = sierra_patron['fixedFields']['263']['value'].strip()
            default_language = Language.objects.filter(code=pref_language_code).first()
            if not default_language:
                default_language = Language.default()
            patron = Patron(
                patron_record_number=patron_record_number,
                pickup_location=pickup_location,
                default_format=default_format,
                default_language=default_language
            )
            patron.save()
        return patron

    def __str__(self):
        return ".p{}a".format(self.patron_record_number)


class Registration(models.Model):
    patron = models.ForeignKey(Patron, models.CASCADE)
    author = models.ForeignKey(Author, models.CASCADE)
    format = models.ForeignKey(Format, models.PROTECT)
    language = models.ForeignKey(Language, models.PROTECT)
    hold_queue_order = models.IntegerField()

    def __str__(self):
        return 'Patron .p{}a for author {}, format {}, language {}, queue pos {}'.format(
            self.patron.patron_record_number,
            self.author.name,
            self.format.code,
            self.language.code,
            self.hold_queue_order
        )

    def move_to_last_in_hold_queue_order(self):
        self.hold_queue_order = RawSQL(
            'SELECT hold_queue_order + 1 '
            'FROM patron_registration '
            'WHERE author_id = %s AND format_id = %s AND language_id = %s '
            'ORDER BY hold_queue_order DESC '
            'LIMIT 1',
            (self.author_id, self.format_id, self.language_id)
        )
        self.save()
        self.refresh_from_db()
