from __future__ import unicode_literals
import json, xml
import lxml
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from bs4 import BeautifulSoup
from django.utils.dateparse import parse_datetime
from reporter.models import Ecu
from unidecode import unidecode


class UdsDatabase(models.Model):
    file = models.FileField(upload_to='static/uploads/ddt2000/ecus/')
    ecu = models.ForeignKey('reporter.Ecu', on_delete=models.CASCADE, editable=False)
    version = models.CharField(max_length=255, editable=False)
    supplier = models.CharField(max_length=255, editable=False)
    default = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'UDS Database'
        unique_together = ("ecu", "version")
    
    def __unicode__(self):
        return unicode(self.ecu) + ' - ' + unicode(self.version)
    
    @receiver(pre_save, sender='reporter.UdsDatabase')
    def parse_file(sender, instance, signal, **kwargs):
        f = instance.file
        f.open()
        db = BeautifulSoup(f.read(), "xml")
        instance.ecu, created = Ecu.objects.get_or_create(name=unidecode(db.find('Function')['Name']).upper())
        instance.supplier = db.find('AutoIdent')['Supplier']
        instance.version = db.find('AutoIdent')['Version']

    @receiver(post_save, sender='reporter.UdsDatabase')
    def import_data(sender, instance, created, signal, **kwargs):    
        if created:
            f = instance.file
            f.open()
            db = BeautifulSoup(f.read(), "xml")
            # Data
            for db_item in db.find_all('Item'):
                # Type
                type, created = UdsDatabaseObjectType.objects.get_or_create(name=db_item.find_parent('Data')['Name'])
                # Item
                UdsDatabaseDefinitionEntry.objects.get_or_create(
                    database=instance,
                    type=type,
                    value=db_item['Value'],
                    text=db_item['Text']
                )
            # Requests 
            for request in db.find_all('Request'):
                received_data_name = None
                received_data_first_byte = None
                received_data_bit_offset = None
                if request.find('DataItem'):
                    received_data_name=request.find('DataItem')['Name']
                    received_data_first_byte=request.find('DataItem')['FirstByte']
                    received_data_bit_offset=request.find('DataItem').get('BitOffset', None)
                
                EcuRequest.objects.get_or_create(
                    database=instance,
                    name=request['Name'],
                    sent_bytes=request.find('SentBytes').string,
                    received_minbytes=request.find('Received')['MinBytes'],
                    received_bytes=request.find('ReplyBytes').string,
                    received_data_name=received_data_name,
                    received_data_first_byte=received_data_first_byte,
                    received_data_bit_offset=received_data_bit_offset
                )
        # Reset the default database
        if not UdsDatabase.objects.filter(ecu=instance.ecu, default=True).exists():
            instance.default = True
            instance.save()
        if instance.default:
            for db in UdsDatabase.objects.filter(ecu=instance.ecu, default=True).exclude(pk=instance.pk).all():
                db.default = False
                db.save()


class UdsDatabaseObjectType(models.Model):
    name = models.CharField(max_length=255)
    
    class Meta:
        verbose_name = 'UDS Database Object Type'
    
    def __unicode__(self):
        return unicode(self.name)


class UdsDatabaseDefinitionEntry(models.Model):
    database = models.ForeignKey('reporter.UdsDatabase', on_delete=models.CASCADE, blank=True, null=True)
    type = models.ForeignKey('reporter.UdsDatabaseObjectType', on_delete=models.CASCADE)
    value = models.FloatField()
    text = models.CharField(max_length=255)
    
    class Meta:
        verbose_name = 'UDS Database Definition Entry'
        verbose_name_plural = 'UDS Database Definition Entries'


class UdsDatabaseValueEntry(models.Model):
    dtc_snapshot = models.ForeignKey('reporter.DtcSnapshot', on_delete=models.CASCADE)
    type = models.ForeignKey('reporter.UdsDatabaseObjectType', on_delete=models.PROTECT)
    value = models.FloatField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'UDS Database Value Entry'
        verbose_name_plural = 'UDS Database Value Entries'
    
    def __unicode__(self):
        return unicode(self.type)
    
    @property
    def text(self):
        try:
            return UdsDatabaseDefinitionEntry.objects.get(database=self.dtc_snapshot.ecu_snapshot.uds_database, type=self.type , value=self.value).text
        except:
            return 'N/A'


class EcuRequest(models.Model):
    database = models.ForeignKey('reporter.UdsDatabase', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    sent_bytes = models.CharField(max_length=255)
    received_minbytes = models.IntegerField()
    received_bytes = models.CharField(max_length=255)
    received_data_name = models.CharField(max_length=255, null=True, blank=True)
    received_data_first_byte = models.IntegerField(null=True, blank=True)
    received_data_bit_offset = models.IntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'ECU Request'
    
    def __unicode__(self):
        return unicode(self.name)
    