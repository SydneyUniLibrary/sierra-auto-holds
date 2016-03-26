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
