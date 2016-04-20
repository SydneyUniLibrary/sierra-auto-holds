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


from base64 import b64encode
from datetime import datetime, timezone

import requests


class SierraApiError(Exception):

    def __init__(self, **kwargs):
        self.http_status = kwargs.get('httpStatus', kwargs.get('http_status', None))
        self.name = kwargs.get('name', None)
        self.code = kwargs.get('code', None)
        self.description = kwargs.get('description', None)
        self.specific_code = kwargs.get('specificCode', kwargs.get('specific_code', None))

    def __str__(self):
        if self.description:
            return '%s (name: %s, code: %s, specific code: %s, http status: %s)' % (
                self.description, self.name, self.code, self.specific_code, self.http_status
            )
        else:
            return '%s (code: %s, specific code: %s, http status: %s)' % (
                self.name, self.code, self.specific_code, self.http_status
            )


class SierraApi_v3:

    @staticmethod
    def login(base_url, client_key, client_secret):
        sierra_api = SierraApi_v3(base_url)
        access_token = sierra_api._do_login(client_key, client_secret)
        sierra_api._do_attach(access_token)
        return sierra_api

    @staticmethod
    def attach(base_url, access_token):
        sierra_api = SierraApi_v3(base_url)
        sierra_api._do_attach(access_token)
        return sierra_api

    def __init__(self, base_url):
        self.base_url = base_url
        self._session = requests.session()
        self.access_token = None

    def _absolute_url(self, relative_url):
        return self.base_url + relative_url

    def _do_login(self, client_key, client_secret):
        encoded_secret = b64encode('{}:{}'.format(client_key, client_secret).encode()).decode()
        response = self._session.post(
            self._absolute_url('/v3/token'),
            headers={'Authorization': 'Basic ' + encoded_secret},
            data={'grant_type': 'client_credentials'}
        )
        response.raise_for_status()
        access_token = response.json()['access_token']
        return access_token

    def _do_attach(self, access_token):
        self.access_token = access_token
        self._session.headers.update({
            'Authorization': 'Bearer {}'.format(access_token),
            'Accept': 'application/json',
        })

    def _get(self, relative_url, params=None):
        return self._session.get(self._absolute_url(relative_url), params=params)

    def _post_json(self, relative_url, json):
        return self._session.post(self._absolute_url(relative_url), json=json)

    def _date_parameter(self, date_spec):
        def _convert_range_part(range_part):
            if range_part is None:
                return ''
            elif isinstance(range_part, datetime):
                return range_part.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            else:
                return str(range_part)
        if isinstance(date_spec, dict):
            range_from = _convert_range_part(date_spec.get('range_from'))
            range_to = _convert_range_part(date_spec.get('range_to', ''))
            return '[{},{}]'.format(range_from, range_to)
        else:
            return str(date_spec)

    def bibs_get(self, *, limit=None, offset=None, fields=None, created_date=None, deleted=None, suppressed=None):
        params = dict()
        if limit is not None:
            params['limit'] = int(limit)
        if offset is not None:
            params['offset'] = int(offset)
        if fields is not None:
            params['fields'] = str(fields)
        if created_date is not None:
            params['createdDate'] = self._date_parameter(created_date)
        if deleted is not None:
            params['deleted'] = bool(deleted)
        if suppressed is not None:
            params['suppressed'] = bool(suppressed)
        response = self._get('/v3/bibs', params)
        if response.status_code == 200:
            return response.json()
        else:
            raise SierraApiError(**response.json())

    def bibs_get_for_id(self, bib_id, *, fields=None):
        params = None if fields is None else {'fields': fields}
        response = self._get('/v3/bibs/{}'.format(bib_id), params)
        if response.status_code == 200:
            return response.json()
        else:
            raise SierraApiError(**response.json())

    def patrons_find(self, barcode, *, fields):
        params = {'barcode': str(barcode)}
        if fields is not None:
            params['fields'] = str(fields)
        response = self._get('/v3/patrons/find', params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return
        else:
            raise SierraApiError(**response.json())

    def patrons_place_hold(self, patron_rec_num, record_type, record_rec_num, pickup_location):
        json = {
            'recordType': str(record_type),
            'recordNumber': int(record_rec_num),
            'pickupLocation': str(pickup_location)
        }
        response = self._post_json('/v3/patrons/{}/holds/requests'.format(patron_rec_num), json)
        if response.status_code == 200:
            return
        else:
            raise SierraApiError(**response.json())
