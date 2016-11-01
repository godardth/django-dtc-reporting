from __future__ import unicode_literals
from django.db import models


class VehicleModel(models.Model):
    brand = models.CharField(max_length=25, null=True, blank=True)
    model = models.CharField(max_length=25, null=True, blank=True)
    class Meta:
        pass
    def __unicode__(self):
        return unicode(self.brand) + ' ' + unicode(self.model)
 

class Vehicle(models.Model):
    vin = models.CharField(max_length=25, primary_key=True)
    model = models.ForeignKey('reporter.VehicleModel', on_delete=models.CASCADE, blank=True, null=True)
    production_date = models.DateTimeField(null=True, blank=True)
    sale_date = models.DateTimeField(null=True, blank=True)
    class Meta:
        pass
    def __unicode__(self):
        return unicode(self.vin)
        
    def _get_report_count(self):
        return self.vehiclesnapshot_set.count()
    report_count = property(_get_report_count)
    

class Ecu(models.Model):
    name = models.CharField(max_length=150)
    acronym = models.CharField(max_length=15, null=True, blank=True)
    class Meta:
        verbose_name = 'ECU'
        verbose_name_plural = 'ECU'
    def __unicode__(self):
        return unicode(self.name)