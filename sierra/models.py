from django.db import models
from .schema import hook_up_set_search_path


hook_up_set_search_path()


class LanguagePropertyMyuser(models.Model):
    code = models.TextField(max_length=3, primary_key=True)
    display_order = models.IntegerField(unique=True)
    is_public = models.BooleanField()
    name = models.TextField(max_length=255)

    class Meta:
        managed = False
        db_table = 'language_property_myuser'

    def __str__(self):
        return '{}:{}'.format(self.code, self.name)

    def __repr__(self):
        return 'LanguagePropertyMyuser(code=%r, display_order=%r, is_public=%r, name=%r)' % (
            self.code, self.display_order, self.is_public, self.name
        )


class LocationMyuser(models.Model):
    code = models.TextField(max_length=5, primary_key=True)
    is_public = models.BooleanField()
    name = models.TextField(max_length=255)

    class Meta:
        managed = False
        db_table = 'location_myuser'

    def __str__(self):
        return '{}:{}'.format(self.code, self.name)

    def __repr__(self):
        return 'LocationMyuser(code=%r, is_public=%r, name=%r)' % (
            self.code, self.is_public, self.name
        )


class MaterialPropertyMyuser(models.Model):
    code = models.TextField(max_length=3, primary_key=True)
    display_order = models.IntegerField(unique=True)
    is_public = models.BooleanField()
    name = models.TextField(max_length=255)

    class Meta:
        managed = False
        db_table = 'material_property_myuser'

    def __str__(self):
        return '{}:{}'.format(self.code, self.name)

    def __repr__(self):
        return 'MaterialPropertyMyuser(code=%r, display_order=%r, is_public=%r, name=%r)' % (
            self.code, self.display_order, self.is_public, self.name
        )
