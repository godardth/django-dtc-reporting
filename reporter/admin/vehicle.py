from django.contrib import admin
from reporter import models


@admin.register(models.VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Ecu)
class EcuAdmin(admin.ModelAdmin):
    pass
