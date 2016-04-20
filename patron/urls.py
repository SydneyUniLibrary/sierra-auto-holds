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

from django.conf.urls import url

from . import views

app_name = 'patron'

urlpatterns = [
    url(r'login$', views.login, name='login'),
    url(r'logout$', views.logout, name='logout'),
    url(r'add_registration$', views.add_registration, name='add_registration'),
    url(r'change_default_format$', views.change_default_format, name='change_default_format'),
    url(r'change_default_language$', views.change_default_language, name='change_default_language'),
    url(r'change_pickup_location$', views.change_pickup_location, name='change_pickup_location'),
    url(r'remove_registration$', views.remove_registration, name='remove_registration'),
    url(r'$', views.account, name='account'),
]
