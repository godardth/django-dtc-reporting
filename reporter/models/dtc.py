from __future__ import unicode_literals
from django.db import models
from reporter.models import Vehicle


class Dtc(models.Model):
    ecu = models.ForeignKey('reporter.Ecu', on_delete=models.CASCADE)
    device_identifier = models.PositiveIntegerField()
    failure_type = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ("device_identifier", "failure_type")
        verbose_name = 'Diagnostic Trouble Code'
    
    def __str__(self):
        return '0x' + hex(self.device_identifier).upper()[2:] + hex(self.failure_type).upper()[2:]
    
    @property 
    def name(self):
        return self.__str__()
    
    @property
    def failure_report_count(self):
        return self.dtcsnapshot_set.count()
        
    @property
    def vehicle_count(self):
        return Vehicle.objects.distinct().filter(vehiclesnapshot__ecusnapshot__dtcsnapshot__dtc=self).count()