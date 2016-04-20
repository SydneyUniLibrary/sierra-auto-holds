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


# TODO: Copy this file to sierrasettings.py and
# edit the setting towards the bottom of this file


class SierraApiSettings:

    def __init__(self, **kwargs):
        self.base_url = kwargs['base_url']
        self.client_key = kwargs['client_key']
        self.client_secret = kwargs['client_secret']

    def __str__(self):
        return str(self.base_url)

    def __repr__(self):
        return 'SierraApiSettings(base_url=%r)' % self.base_url


class SierraSqlSettings:

    def __init__(self, **kwargs):
        self.host = kwargs['host']
        self.port = kwargs['port']
        self.user = kwargs['user']
        self.password = kwargs['password']

    def __str__(self):
        return str(self.host)

    def __repr__(self):
        return 'SierraSqlSettings(host=%r, port=%r)' % (self.host, self.port)


SIERRA_API = SierraApiSettings(
        base_url='''https://sierra-app-server.mylibrary.url/iii/sierra-api''',
        client_key='''key''',
        client_secret='''secret''',
)


SIERRA_SQL = SierraSqlSettings(
    host='''sierra-db-server.mylibrary.url''',
    port=1032,
    user='''autoholds''',
    password='''pass''',
)
