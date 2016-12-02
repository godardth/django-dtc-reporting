from django.contrib import admin
from reporter import models


@admin.register(models.Dtc)
class DtcAdmin(admin.ModelAdmin):
    pass