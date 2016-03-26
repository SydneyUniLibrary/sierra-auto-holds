from django.contrib import admin

from .models import Author, Format, Language, PickupLocation, Patron, Registration

admin.site.register(Author)
admin.site.register(Format)
admin.site.register(Language)
admin.site.register(PickupLocation)
admin.site.register(Patron)
admin.site.register(Registration)
