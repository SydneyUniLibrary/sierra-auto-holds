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


from django.db.backends.signals import connection_created


def set_search_path(sender, **kwargs):
    conn = kwargs.get('connection')
    if conn is not None:
        conn_params = conn.get_connection_params()
        conn_database = conn_params.get('database')
        conn_port = conn_params.get('port')
        if conn_database == 'iii' and conn_port == 1032:
            cursor = conn.cursor()
            cursor.execute("SET search_path=sierra_view")


def hook_up_set_search_path():
    connection_created.connect(set_search_path)
