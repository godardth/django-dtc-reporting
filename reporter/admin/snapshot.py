from django.contrib import admin
from reporter.models import VehicleSnapshot, EcuSnapshot, DtcSnapshot


class VehicleSnapshotAdmin(admin.ModelAdmin):
    pass


class EcuSnapshotAdmin(admin.ModelAdmin):
    pass


class DtcSnapshotAdmin(admin.ModelAdmin):
    pass


admin.site.register(VehicleSnapshot, VehicleSnapshotAdmin)
admin.site.register(EcuSnapshot, EcuSnapshotAdmin)
admin.site.register(DtcSnapshot, DtcSnapshotAdmin)
