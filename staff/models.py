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


from django.db import models


class Log(models.Model):
    log_created_at = models.DateTimeField(auto_now_add=True, editable=False)
    log_updated_at = models.DateTimeField(auto_now=True, editable=False)
    log_notes = models.TextField(editable=False)

    class Meta:
        abstract = True


class RunLog(Log):
    started_at = models.DateTimeField(editable=False)
    ended_at = models.DateTimeField(null=True, editable=False)
    successful = models.BooleanField(default=False, editable=False)
    num_bibs_found = models.IntegerField(default=0, editable=False)
    first_bib_record_number = models.IntegerField(null=True, editable=False)
    first_bib_created_at = models.DateTimeField(null=True, editable=False)
    last_bib_record_number = models.IntegerField(null=True, editable=False)
    last_bib_created_at = models.DateTimeField(null=True, editable=False)

    class Meta(Log.Meta):
        pass


class BibLog(Log):
    run_log = models.ForeignKey(RunLog, models.CASCADE, editable=False, related_name='bibs_found')
    bib_record_number = models.IntegerField(editable=False)
    bib_created_at = models.DateTimeField(editable=False)
    author = models.CharField(blank=True, max_length=255, editable=False)
    format = models.CharField(blank=True, max_length=1, editable=False)
    language = models.CharField(blank=True, max_length=3, editable=False)
    num_registrations_found = models.IntegerField(default=0, editable=False)

    class Meta(Log.Meta):
        pass


class HoldLog(Log):
    bib_log = models.ForeignKey(BibLog, models.CASCADE, editable=False, related_name='holds_placed')
    patron_record_number = models.IntegerField(editable=False)
    pickup_location = models.CharField(blank=True, max_length=5, editable=False)
    successful = models.BooleanField(default=False, editable=False)

    class Meta(Log.Meta):
        pass
