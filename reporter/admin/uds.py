from django.contrib import admin
from reporter import models


@admin.register(models.UdsDatabase)
class UdsDatabaseAdmin(admin.ModelAdmin):
    list_display = ('ecu', 'supplier', 'version', 'default')
    search_fields = ['ecu', 'supplier', 'version']


@admin.register(models.UdsDatabaseObjectType)
class UdsDatabaseObjectTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name']


@admin.register(models.UdsDatabaseDefinitionEntry)
class UdsDatabaseDefinitionEntryAdmin(admin.ModelAdmin):
    list_display = ('database', 'type', 'value', 'text')
    search_fields = ['database', 'type', 'value', 'text']


@admin.register(models.UdsDatabaseValueEntry)
class UdsDatabaseValueEntryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'date', 'vehicle', 'ecu', 'dtc_snapshot', 'type', 'value', 'text')
    search_fields = ['pk', 'date', 'vehicle', 'ecu', 'dtc_snapshot', 'type', 'value']
    # Vehicle
    def vehicle(self, obj):
        return obj.dtc_snapshot.ecu_snapshot.vehicle_snapshot.vehicle.vin
    vehicle.short_description = 'VIN'
    vehicle.admin_order_field = 'dtc_snapshot__ecu_snapshot__vehicle_snapshot__vehicle__vin'
    # Date
    def date(self, obj):
        return obj.dtc_snapshot.ecu_snapshot.vehicle_snapshot.captured_on
    date.short_description = 'Date'
    date.admin_order_field = 'dtc_snapshot__ecu_snapshot__vehicle_snapshot__captured_on'
    # ECU
    def ecu(self, obj):
        return obj.dtc_snapshot.ecu_snapshot.ecu
    ecu.short_description = 'ECU'
    ecu.admin_order_field = 'dtc_snapshot__ecu_snapshot__ecu'


@admin.register(models.EcuRequest)
class EcuRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'received_data_name')
    search_fields = ['name', 'received_data_name']