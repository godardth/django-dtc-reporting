from django.contrib import admin
from reporter.models import UdsDatabase, UdsDatabaseObjectType, UdsDatabaseDefinitionEntry, UdsDatabaseValueEntry, EcuRequest


class UdsDatabaseAdmin(admin.ModelAdmin):
    pass
admin.site.register(UdsDatabase, UdsDatabaseAdmin)

class UdsDatabaseObjectTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name']
admin.site.register(UdsDatabaseObjectType, UdsDatabaseObjectTypeAdmin)


class UdsDatabaseDefinitionEntryAdmin(admin.ModelAdmin):
    list_display = ('database', 'type', 'value', 'text')
    search_fields = ['database', 'type', 'value', 'text']
admin.site.register(UdsDatabaseDefinitionEntry, UdsDatabaseDefinitionEntryAdmin)


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
admin.site.register(UdsDatabaseValueEntry, UdsDatabaseValueEntryAdmin)


class EcuRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'received_data_name')
    search_fields = ['name', 'received_data_name']
admin.site.register(EcuRequest, EcuRequestAdmin)