from django.contrib import admin
from reporter import models


@admin.register(models.VehicleSnapshot)
class VehicleSnapshotAdmin(admin.ModelAdmin):
    pass


@admin.register(models.EcuSnapshot)
class EcuSnapshotAdmin(admin.ModelAdmin):
    list_display = ('pk', 'date', 'vehicle', 'ecu')
    search_fields = ['pk', 'date', 'vehicle', 'ecu']
    # Date
    def date(self, obj):
        return obj.vehicle_snapshot.captured_on
    date.short_description = 'Captured on'
    date.admin_order_field = 'vehicle_snapshot__captured_on'
    # Vehicle
    def vehicle(self, obj):
        return obj.vehicle_snapshot.vehicle.vin
    vehicle.short_description = 'VIN'
    vehicle.admin_order_field = 'vehicle_snapshot__vehicle__vin'


@admin.register(models.DtcSnapshot)
class DtcSnapshotAdmin(admin.ModelAdmin):
    list_display = ('pk', 'date', 'vehicle', 'ecu', '__unicode__')
    search_fields = ['pk', 'date', 'vehicle', 'ecu',]
    # Vehicle
    def vehicle(self, obj):
        return obj.ecu_snapshot.vehicle_snapshot.vehicle.vin
    vehicle.short_description = 'VIN'
    vehicle.admin_order_field = 'ecu_snapshot__vehicle_snapshot__vehicle__vin'
    # Date
    def date(self, obj):
        return obj.ecu_snapshot.vehicle_snapshot.captured_on
    date.short_description = 'Captured on'
    date.admin_order_field = 'ecu_snapshot__vehicle_snapshot__captured_on'
    # ECU
    def ecu(self, obj):
        return obj.ecu_snapshot.ecu
    ecu.short_description = 'ECU'
    ecu.admin_order_field = 'ecu_snapshot__ecu'
