from django.contrib import admin
from reporter.models import UdsDatabaseObjectType, UdsDatabaseDefinitionEntry, UdsDatabaseValueEntry


class UdsDatabaseObjectTypeAdmin(admin.ModelAdmin):
    pass


class UdsDatabaseDefinitionEntryAdmin(admin.ModelAdmin):
    pass


class UdsDatabaseValueEntryAdmin(admin.ModelAdmin):
    pass


admin.site.register(UdsDatabaseObjectType, UdsDatabaseObjectTypeAdmin)
admin.site.register(UdsDatabaseDefinitionEntry, UdsDatabaseDefinitionEntryAdmin)
admin.site.register(UdsDatabaseValueEntry, UdsDatabaseValueEntryAdmin)
