from django.contrib import admin
from reporter.models import Dtc


class DtcAdmin(admin.ModelAdmin):
    pass
admin.site.register(Dtc, DtcAdmin)