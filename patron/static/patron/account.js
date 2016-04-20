/*
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
*/


'use strict';


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrfToken;

function onHelpIconClick() {
    var dataHelpFor = $(this).attr('data-help-for');
    var elem = $('#' + dataHelpFor);
    elem.tooltip();
}

function onPickupLocationChange() {
    var newId = $(this).val();
    postChange(
        '/patron/change_pickup_location',
        newId,
        'We successfully changed your pickup location.',
        'Sorry. Something went wrong when we tried to change your pickup location.',
        'Pickup Location'
);
}

function onDefaultFormatChange() {
    var newId = $(this).val();
    postChange(
        '/patron/change_default_format',
        newId,
        'We successfully changed your preferred format.',
        'Sorry. Something went wrong when we tried to change your preferred format.',
        'Preferred Format'
    );
    $('#add-format').find('option[value="' + newId + '"]').prop("selected", "selected");
}

function onDefaultLanguageChange() {
    var newId = $(this).val();
    postChange(
        '/patron/change_default_language',
        newId,
        'We successfully changed your preferred language.',
        'Sorry. Something went wrong when we tried to change your preferred language.',
        'Preferred Language'
    );
    $('#add-language').find('option[value="' + newId + '"]').prop("selected", "selected");
}

function onRemoveButtonClick() {
    var dataRemoveButton = $(this).attr('data-remove-button');
    $('#remove-form-id').val(dataRemoveButton);
    $('#remove-form').submit();
}

function postChange(url, newId, successText, failureText, toastHeading) {
    $.ajax({
        'url': url,
        'data': { 'id': newId },
        'method': 'POST',
        'dataType': 'json',
        'headers': { 'X-CSRFToken': csrfToken }
    }).done(function(data) {
        if (data.ok) {
            showToast('success', successText, toastHeading);
        } else {
            showToast('error', failureText, toastHeading);
        }
    }).fail(function() {
        showToast('error', failureText, toastHeading);
    });
}

function showToast(icon, text, heading) {
    var hideAfter = (icon == 'success' || icon == 'info') ? 3000: 6000;
    $.toast({
        'text': text,
        'heading': heading,
        'icon': icon,
        'showHideTransition': 'slide',
        'allowToastClose': true,
        'hideAfter': hideAfter,
        'position': 'top-center',
        'loader': false,
        'stack': 2
    });
}

$(function () {
    csrfToken = getCookie('csrftoken');
    $('[data-toggle="tooltip"]').tooltip();
    $('[data-help-for]').on('click', onHelpIconClick);
    $('[data-remove-button]').on('click', onRemoveButtonClick);
    $('#pickup-location').on('change', onPickupLocationChange);
    $('#default-format').on('change', onDefaultFormatChange)
    $('#default-language').on('change', onDefaultLanguageChange)
})
