from django.contrib import admin
from reporter.models import Vehicle, Ecu


class VehicleAdmin(admin.ModelAdmin):
    pass


class EcuAdmin(admin.ModelAdmin):
    pass


admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Ecu, EcuAdmin)
