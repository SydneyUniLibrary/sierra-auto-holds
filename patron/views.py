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
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from patron.models import Author, Format, Language, Patron, PickupLocation, Registration
from sierra.api import SierraApi_v2


def account(request):
    patron = _patron_in_session(request)
    registrations = patron.registration_set.order_by('author__friendly_name', 'format__value', 'language__name')
    return render(
        request, 'patron/account.html',
        context={
            'authors': Author.objects.all().order_by('friendly_name'),
            'formats': Format.objects.filter(active=True).order_by('value'),
            'languages': Language.objects.filter(active=True).order_by('name'),
            'patron': patron,
            'patron_name': _patron_name_in_session(request),
            'pickup_locations': PickupLocation.objects.filter(active=True).order_by('name'),
            'registrations': registrations,
        }
    )


def add_registration(request):
    author_id = int(request.POST['author'])
    format_id = int(request.POST['format'])
    language_id = int(request.POST['language'])
    if author_id == 0:
        messages.info(request, 'Select an author before you try to add an auto-hold.')
    else:
        patron_obj = _patron_in_session(request)
        author_obj = Author.objects.get(pk=author_id)
        format_obj = Format.objects.get(pk=format_id)
        language_obj = Language.objects.get(pk=language_id)
        reg = Registration(
                patron=patron_obj,
                author=author_obj,
                format=format_obj,
                language=language_obj,
                hold_queue_order=1
            )
        reg.save()
        reg.move_to_last_in_hold_queue_order()
        messages.success(request, 'We successfully added the auto-hold.')
    return HttpResponseRedirect(reverse('patron:account'))


@require_http_methods(['POST'])
def change_default_format(request):
    id_param = request.POST['id']
    new_format = Format.objects.get(pk=id_param)
    patron = _patron_in_session(request)
    patron.default_format = new_format
    patron.save()
    return JsonResponse({'ok': True})


@require_http_methods(['POST'])
def change_default_language(request):
    id_param = request.POST['id']
    new_language = Language.objects.get(pk=id_param)
    patron = _patron_in_session(request)
    patron.default_language = new_language
    patron.save()
    return JsonResponse({'ok': True})


@require_http_methods(['POST'])
def change_pickup_location(request):
    id_param = request.POST['id']
    pickup_location = PickupLocation.objects.get(pk=id_param)
    patron = _patron_in_session(request)
    patron.pickup_location = pickup_location
    patron.save()
    return JsonResponse({'ok': True})


def login(request):
    try:
        barcode = request.POST['barcode']
    except KeyError:
        return render(request, 'patron/login.html')
    barcode = barcode.strip()
    if not barcode:
        messages.info(request, 'Enter your barcode before trying to log in.')
        return render(request, 'patron/login.html')
    sierra_api = _sierra_api_in_session(request)
    sierra_patron = sierra_api.patrons_find(barcode, fields='id,names,fixedFields')
    if not sierra_patron:
        messages.info(request, 'The barcode you entered seems to be incorrect.')
        return render(request, 'patron/login.html')
    autoholds_patron = Patron.for_sierra_patron(sierra_patron)
    request.session['patron_id'] = autoholds_patron.id
    request.session['patron_name'] = sierra_patron['names'][0]
    messages.info(request, 'You successfully logged in.')
    return HttpResponseRedirect(reverse('patron:account'))


def logout(request):
    request.session.clear()
    return HttpResponseRedirect(reverse('patron:login'))


def redirect_to_login(request):
    return HttpResponseRedirect(reverse('patron:login'))


def remove_registration(request):
    reg_id = request.POST['id']
    reg = Registration.objects.get(pk=reg_id)
    reg.delete()
    messages.success(request, 'We successfully removed the auto-hold.')
    return HttpResponseRedirect(reverse('patron:account'))


def _sierra_api_in_session(request):
    try:
        access_token = request.session['sierra_api_access_token']
        return SierraApi_v2.attach(settings.SIERRA_API.base_url, access_token)
    except KeyError:
        sierra_api = SierraApi_v2.login(
            settings.SIERRA_API.base_url,
            settings.SIERRA_API.client_key,
            settings.SIERRA_API.client_secret
        )
        request.session['sierra_api_access_token'] = sierra_api.access_token
        return sierra_api


def _patron_in_session(request):
    return Patron.objects.get(pk=request.session['patron_id'])


def _patron_name_in_session(request):
    try:
        return request.session['patron_name']
    except KeyError:
        return 'Sir/Madam'
