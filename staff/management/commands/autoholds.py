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


import sys
import traceback

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import localtime, now

from patron.models import Registration
from sierra.api import SierraApi_v2, SierraApiError
from ...models import BibLog, HoldLog, RunLog


class Command(BaseCommand):

    help = 'Discover new bib records and place auto-holds on them'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sierra_api = None

    def handle(self, *args, **options):
        run_log = RunLog(started_at=now())
        run_log.save()
        try:
            self.stdout.write('This run will be recorded into run log id {}'.format(run_log.id))
            self.sierra_api = SierraApi_v2.login(
                settings.SIERRA_API.base_url,
                settings.SIERRA_API.client_key,
                settings.SIERRA_API.client_secret
            )
            last_bib_record_number, last_bib_created_at = self._last_bib_seen()
            self._log_info(
                run_log,
                'The last bib that was seen in previous runs was .b{}a, created at {}.',
                last_bib_record_number, localtime(last_bib_created_at)
            )
            new_bibs = self._get_new_bibs(last_bib_created_at, run_log.started_at)
            # new_bibs = self._get_bibs(4862249, 4862252, 4862294)
            run_log.num_bibs_found = len(new_bibs)
            self._log_info(
                run_log,
                'Found {} new bib records created since {}',
                run_log.num_bibs_found, localtime(last_bib_created_at)
            )
            for bib in new_bibs:
                try:
                    bib_record_number = int(bib['id'])
                except ValueError as e:
                    self._log_error(
                        run_log,
                        'Failed to convert bib id {} to an integer: {}',
                        bib.get('id', '?'), e
                    )
                    self._log_exception_details(run_log, sys.exc_info())
                    continue
                if bib_record_number <= last_bib_record_number:
                    self._log_notice(
                        run_log,
                        'Skipping .b{}a because it has already seen during a previous run',
                        bib_record_number
                    )
                    continue
                try:
                    self._process_bib(bib, bib_record_number, run_log)
                except Exception as e:
                    self._log_error(
                        run_log,
                        'An error occurred while processing .b{}a: {}',
                        bib_record_number, e
                    )
                    self._log_exception_details(run_log, sys.exc_info())
        except Exception as e:
            self._log_error(run_log, 'An error occurred while autoholds was running: {}', e)
            self._log_exception_details(run_log, sys.exc_info())
        else:
            run_log.successful = True
        finally:
            run_log.ended_at = now()
            run_log.save()

    def _last_bib_seen(self):
        #
        # Resume find the bib record with the highest id that we've seen previously, and resume from it's creation date.
        #
        try:
            last_biblog = BibLog.objects.order_by('-bib_created_at')[0]
            last_bib_record_number = last_biblog.bib_record_number
            last_bib_created_at = last_biblog.bib_created_at
        except IndexError:
            last_bib_record_number = 0
            last_bib_created_at = None
        #
        # If we have not seen any bib records before, resume from when we last finished running.
        # Note: By this point we have already inserted the run log for this current run. So the run log for run previous
        # to this one is now the second last run in the database when order by ended_at.
        #
        if last_bib_created_at is None:
            try:
                last_runlog = RunLog.objects.order_by('-ended_at')[1]
                last_bib_created_at = last_runlog.ended_at
            except IndexError:
                last_bib_created_at = None
        #
        # If there are no previous runs, resume from now.
        #
        if last_bib_created_at is None:
            last_bib_created_at = now()
        #
        return last_bib_record_number, last_bib_created_at

    def _process_bib(self, bib, bib_record_number, run_log):
        bib_log = BibLog(
            run_log=run_log,
            bib_record_number=bib_record_number,
            bib_created_at=self.sierra_api.parse_datetime(bib['createdDate']),
            author=bib['author'],
            format=bib['materialType']['code'],
            language=bib['lang']['code']
        )
        bib_log.save()
        try:
            if bib_log.author:
                regs = (
                    Registration.objects.filter(
                        author__name__iexact=bib_log.author,
                        format__code=bib_log.format,
                        format__active=True,
                        language__code=bib_log.language,
                        language__active=True
                    )
                    .order_by('hold_queue_order')
                )
                bib_log.num_registrations_found = len(regs)
                self._log_info(
                    bib_log,
                    'Found {} registrations for .b{}a, format {} and language {}',
                    bib_log.num_registrations_found, bib_record_number, bib_log.format, bib_log.language
                )
                for reg in regs:
                    try:
                        self._place_hold(bib_record_number, reg, bib_log)
                    except Exception as e:
                        self._log_error(
                            bib_log,
                            'An error occurred while processing registration id {} for .b{}a: {}',
                            reg.id, bib_record_number, e
                        )
                        self._log_exception_details(bib_log, sys.exc_info())
                if len(regs) > 1:
                    first_reg = regs[0]
                    first_reg.move_to_last_in_hold_queue_order()
                    self._log_info(
                        bib_log,
                        'Moved .p{}a to bottom of queue for .b{}a, format {} and language {}. New position is {}',
                        first_reg.patron.patron_record_number, bib_record_number, bib_log.format,
                        bib_log.language, first_reg.hold_queue_order
                    )
            else:
                self._log_notice(
                    bib_log,
                    'Skipping .b{}a because it has no author',
                    bib_record_number
                )
        except Exception as e:
            self._log_error(
                bib_log,
                'An error occurred while processing .b{}a: {}',
                bib.get('id', '?'), e
            )
            self._log_exception_details(bib_log, sys.exc_info())
        finally:
            bib_log.save()

    def _place_hold(self, bib_record_number, registration, bib_log):
        hold_log = HoldLog(
            bib_log=bib_log,
            patron_record_number=registration.patron.patron_record_number,
            pickup_location=registration.patron.pickup_location.code
        )
        try:
            self.sierra_api.patrons_place_hold(
                hold_log.patron_record_number,
                'b',
                bib_record_number,
                hold_log.pickup_location
            )
        except SierraApiError as e:
            self._log_warning(
                hold_log,
                'Failed to place hold on .b{}a for .p{}a (registration id {}): {}',
                bib_record_number, hold_log.patron_record_number, registration.id, e
            )
        except Exception as e:
            self._log_error(
                hold_log,
                'An error occurred while processing registration id {} for .b{}a: {}',
                registration.id, bib_record_number, e
            )
            self._log_exception_details(hold_log, sys.exc_info())
        else:
            self._log_success(
                hold_log,
                'Successfully placed hold on .b{}a for .p{}a with pickup at {} (registration id {})',
                bib_record_number, hold_log.patron_record_number, hold_log.pickup_location, registration.id
            )
            hold_log.successful = True
        finally:
            hold_log.save()

    def _get_bibs(self, *bib_ids):
        result = list()
        for bib_id in bib_ids:
            result.append(self.sierra_api.bibs_get_for_id(bib_id, fields='id,author,materialType,lang,createdDate'))
        return result

    def _get_new_bibs(self, created_date_from, created_date_to):
        result = self.sierra_api.bibs_get(
            created_date={'range_from': created_date_from, 'range_to': created_date_to},
            fields='id,author,materialType,lang,createdDate',
            deleted=False,
            suppressed=False
        )
        return result['entries']

    def _log_error(self, log, fmt, *args, **kwargs):
        log_note = fmt.format(*args, **kwargs)
        self.stdout.write(log_note, style_func=self.style.ERROR)
        log.append_log_note('[ERROR] ' + log_note)

    def _log_warning(self, log, fmt, *args, **kwargs):
        log_note = fmt.format(*args, **kwargs)
        self.stdout.write(log_note, style_func=self.style.WARNING)
        log.append_log_note('[WARNING] ' + log_note)

    def _log_notice(self, log, fmt, *args, **kwargs):
        log_note = fmt.format(*args, **kwargs)
        self.stdout.write(log_note, style_func=self.style.NOTICE)
        log.append_log_note('[NOTICE] ' + log_note)

    def _log_info(self, log, fmt, *args, **kwargs):
        log_note = fmt.format(*args, **kwargs)
        self.stdout.write(log_note)
        log.append_log_note('[INFO] ' + log_note)

    def _log_success(self, log, fmt, *args, **kwargs):
        log_note = fmt.format(*args, **kwargs)
        self.stdout.write(log_note, style_func=self.style.SUCCESS)
        log.append_log_note('[SUCCESS] ' + log_note)

    def _log_exception_details(self, log, exec_info):
        a = list()
        a.append('>>>  START OF ERROR DETAILS  >>>\n')
        a.extend(traceback.format_exception(*exec_info))
        a.append('<<<  END OF ERROR DETAILS  <<<')
        log_note = ''.join(a)
        self.stdout.write(log_note, style_func=self.style.ERROR)
        log.append_log_note(log_note)
