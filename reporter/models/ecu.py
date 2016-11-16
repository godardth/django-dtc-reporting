from __future__ import unicode_literals
from django.db import models


class Ecu(models.Model):
    name = models.CharField(max_length=150)
    acronym = models.CharField(max_length=15, null=True, blank=True)
    
    class Meta:
        verbose_name = 'ECU'
        verbose_name_plural = 'ECU'
    
    def __unicode__(self):
        return unicode(self.name)
        
    @property
    def default_database(self):
        return self.udsdatabase_set.get(ecu=self, default=True)