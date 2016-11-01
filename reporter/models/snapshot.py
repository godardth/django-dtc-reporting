from __future__ import unicode_literals
import json
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from reporter.models import Vehicle, Ecu, EcuRequest, UdsDatabaseObjectType, UdsDatabase, UdsDatabaseValueEntry, UdsDatabaseDefinitionEntry, Dtc
from bs4 import BeautifulSoup
from django.utils.dateparse import parse_datetime


class VehicleSnapshot(models.Model):
    # Related objects
    vehicle = models.ForeignKey('reporter.Vehicle', on_delete=models.CASCADE, editable=False)
    # Snapshot Data (Vehicle Level)
    file = models.FileField(upload_to='static/uploads/snapshots/')
    captured_on = models.DateTimeField(null=True, blank=True, editable=False)
    created_on = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Vehicle Snapshot'
        unique_together = ("vehicle", "captured_on")
    
    def __unicode__(self):
        return unicode(self.captured_on)
    
    @property
    def dtc_count(self):
        count = 0
        for ecu in self.ecusnapshot_set.all():
            count += ecu.dtcsnapshot_set.count()
        return count
    
    @receiver(pre_save, sender='reporter.VehicleSnapshot')
    def parse_file(sender, instance, signal, **kwargs):
        # Vehicle Snapshot Parameters Parsing
        f = instance.file
        f.open()
        soup = BeautifulSoup(f.read().encode('utf-8','ignore'), "html5lib")
        instance.captured_on = parse_datetime(soup.select('.tbComment td')[0].string)
        instance.vehicle, created = Vehicle.objects.get_or_create(vin=soup.select('.identification th.fctname')[1].find_all('font')[0].string)
        
    @receiver(post_save, sender='reporter.VehicleSnapshot')
    def create_ecu_snapshot(sender, instance, created, signal, **kwargs):    
        if created:
            # Vehicle Snapshot Parameters Parsing
            f = instance.file
            f.open()
            soup = BeautifulSoup(f.read().encode('utf-8','ignore'), "html5lib")
            # ECU Snapshots
            for ecu_section in soup.select('.identification'):
                ecu_snapshot = EcuSnapshot()
                ecu_snapshot.vehicle_snapshot=instance
                ecu_snapshot.raw=unicode(ecu_section)
                ecu_snapshot.save()


class EcuSnapshot(models.Model):
    # Related objects
    vehicle_snapshot = models.ForeignKey('reporter.VehicleSnapshot', on_delete=models.CASCADE)
    uds_database = models.ForeignKey('reporter.UdsDatabase', on_delete=models.SET_NULL, null=True, blank=True)
    ecu = models.ForeignKey('reporter.Ecu', on_delete=models.CASCADE, null=True, blank=True)
    # Snapshot Data (ECU Level)
    software_name = models.CharField(max_length=15, null=True, blank=True)
    part_reference = models.CharField(max_length=10, null=True, blank=True)
    hardware_reference = models.CharField(max_length=10, null=True, blank=True)
    software_reference = models.CharField(max_length=10, null=True, blank=True)
    calibration_reference = models.CharField(max_length=10, null=True, blank=True)
    software_reference = models.CharField(max_length=10, null=True, blank=True)
    supplier = models.CharField(max_length=200, null=True, blank=True)
    serial_number = models.CharField(max_length=200, null=True, blank=True)
    diag_version = models.CharField(max_length=15, null=True, blank=True)
    raw = None
    
    class Meta:
        verbose_name = 'ECU Snapshot'
        unique_together = ('vehicle_snapshot', 'ecu')
    
    def __unicode__(self):
        return unicode(self.ecu)
        
    @receiver(pre_save, sender='reporter.EcuSnapshot')
    def parse_file(sender, instance, signal, **kwargs):
        if not instance.pk:
            soup = BeautifulSoup(instance.raw, "html5lib")
            instance.ecu, created = Ecu.objects.get_or_create(name=soup.select('.identification th.fctname')[0].find_all('font')[0].string)
            data = soup.select('.identification > tbody > tr > td')
            instance.part_reference = data[1].string
            instance.diag_version = data[2].string
            instance.supplier = data[3].string
            instance.hardware_reference = data[4].string
            instance.software_name = data[5].string
            instance.software_reference = ''
            instance.serial_number = data[11].string
            instance.calibration_reference = data[12].string
    
    @receiver(post_save, sender='reporter.EcuSnapshot')
    def create_dtcsnapshot_snapshot(sender, instance, created, signal, **kwargs):    
        if created:
            soup = BeautifulSoup(instance.raw, "html5lib")
            dtc_snaphots = soup.select('.identification > tbody > tr:nth-of-type(7) > td > table > tbody > tr')
            dtc_snaphots_iter = iter(dtc_snaphots)
            for dtc_section in dtc_snaphots_iter:
                dtc_snapshot = DtcSnapshot()
                dtc_snapshot.ecu_snapshot=instance
                dtc_snapshot.raw=unicode(dtc_section) + unicode(next(dtc_snaphots_iter))
                dtc_snapshot.save()

    
class DtcSnapshot(models.Model):
    # Related objects
    ecu_snapshot = models.ForeignKey('reporter.EcuSnapshot', on_delete=models.CASCADE)
    dtc = models.ForeignKey('reporter.Dtc', on_delete=models.PROTECT, blank=True, null=True)
    # Snapshot Data (DTC Level)
    status_byte = models.PositiveIntegerField(blank=True, null=True)
    status_byte_availabilty_mask = models.PositiveIntegerField(default=0)
    snapshot_data = models.TextField(blank=True, null=True)
    
    raw = None
    status_mask = [
        {'bit': 1, 'state': 'testFailed', 'text': 'B0_ DTCStatus.testFailed'},    
        {'bit': 2, 'state': 'testFailedThisOperationCycle', 'text': ''}, 
        {'bit': 4, 'state': 'pendingDTC', 'text': ''}, 
        {'bit': 8, 'state': 'confirmedDTC', 'text': 'B3_ DTCStatus.confirmedDTC'}, 
        {'bit': 16, 'state': 'testNotCompletedSinceLastClear', 'text': 'B4_ DTCStatus.testNotCompletedSinceLastClear'}, 
        {'bit': 32, 'state': 'testFailedSinceLastClear', 'text': 'B5_ DTCStatus.testFailedSinceLastClear'}, 
        {'bit': 64, 'state': 'testNotCompletedThisOperationCycle', 'text': 'B6_ DTCStatus.testNotCompletedThisMonitoringCycle'}, 
        {'bit': 128, 'state': 'warningIndicatorRequested', 'text': 'B7_ DTCStatus.warningIndicatorRequested'}  
    ]
    
    class Meta:
        verbose_name = 'DTC Snapshot'
    
    def __unicode__(self):
        return '0x' + hex(int(self.device_identifier.value)).upper()[2:] + hex(int(self.failure_type.value)).upper()[2:]
    
    @property
    def device_identifier(self):
        return self.udsdatabasevalueentry_set.get(type__name='DTCDeviceIdentifier')
    
    @property
    def failure_type(self):
        return self.udsdatabasevalueentry_set.get(type__name='DTCFailureType')
    
    @property
    def dtc_status(self):
        status = dict()
        for mask_item in self.status_mask:
            if (self.status_byte_availabilty_mask & mask_item['bit']) / mask_item['bit'] == 1:
                status[mask_item['state']] = (self.status_byte & mask_item['bit']) / mask_item['bit']
            else:
                status[mask_item['state']] = None
        return status
    
    @property
    def snapshot_data_db(self):
        data_db = json.loads(self.snapshot_data)
        ret = dict()
        for k, data_list in data_db.iteritems():
            ret[k] = []
            for data_item in data_list:
                # Request Name
                try:
                    request_db = EcuRequest.objects.get(database=self.ecu_snapshot.uds_database, sent_bytes='220'+hex(data_item['request'])[2:]).received_data_name
                except:
                    request_db = data_item['request']
                # Data Textual
                try:
                    value_db = UdsDatabaseDefinitionEntry.objects.get(database=self.ecu_snapshot.uds_database, value=data_item['value']).text + ' ('+data_item['value']+')'
                except:
                    value_db = data_item['value']
                ret[k].append({'request': data_item['request'], 'request_db': request_db, 'value': data_item['value'], 'value_db': value_db})
        return json.dumps(ret)
        
    @receiver(pre_save, sender='reporter.DtcSnapshot')
    def parse_status_byte(sender, instance, signal, **kwargs):
        if not instance.pk:
            soup = BeautifulSoup(instance.raw, "html5lib")
            summary_line_cells = soup.select('.DTCName > tbody > tr > td')
            summary_table = soup.select('.StatusDTC > tbody')[0]
            if summary_table:
                instance.status_byte = 0
                instance.status_byte_availabilty_mask = 0
                for line in summary_table.select('tr')[1:]:
                    text = line.select('td:nth-of-type(1)')[0].string
                    # In case format mismatch (unexpected space char)
                    try:
                        val = int(line.select('td:nth-of-type(2)')[0].string.split(' ', 1)[0])
                    except ValueError:
                        continue
                    # Normal case (0 or 1 value)
                    for mask_item in instance.status_mask:
                        if mask_item['text'] == text:
                            instance.status_byte += mask_item['bit'] * val
                            instance.status_byte_availabilty_mask += mask_item['bit']
    
    @receiver(post_save, sender='reporter.DtcSnapshot')
    def create_dtcsnapshot_snapshot(sender, instance, created, signal, **kwargs):    
        if created:
            soup = BeautifulSoup(instance.raw, "html5lib")
            summary_line_cells = soup.select('.DTCName > tbody > tr > td')
            # Get the device identifier
            UdsDatabaseValueEntry.objects.create(
                dtc_snapshot=instance,
                type=UdsDatabaseObjectType.objects.get(name='DTCDeviceIdentifier'),
                value=int(summary_line_cells[2].string[1:], 16)
            )
            # Get the Failure Type
            summary_table = soup.select('.StatusDTC > tbody')[0]
            for line in summary_table.select('tr')[1:]:
                text = line.select('td:nth-of-type(1)')[0].string
                if text == 'FailureType':
                    UdsDatabaseValueEntry.objects.create(
                        dtc_snapshot=instance,
                        type=UdsDatabaseObjectType.objects.get(name='DTCFailureType'),
                        value=int(line.select('td:nth-of-type(2)')[0].string.split(' ', 1)[0])
                    )
            # ... from body table
            extradata_table_lines = soup.select_one('.FreezeF > tbody').find_all('tr', recursive=False)
            record = 0
            extradata = dict()
            for line in extradata_table_lines[1:]:
                # If line contains a record number, update record number
                try: 
                    content = line.select('th')[0].string
                    index = content.index('Record : ')
                    record = content[index+9:content.index(' ?(')]
                    extradata[record] = []
                    continue
                except:
                    pass
                # Line is a data line
                datacells = line.select('.FreezeF td')
                extradata[record].append({
                    'request': int(datacells[1].string[1:], 16),
                    'value': datacells[3].string
                })
            instance.snapshot_data = json.dumps(extradata)
            # Create the DTC type if not found
            instance.dtc, created = Dtc.objects.get_or_create(
                ecu=instance.ecu_snapshot.ecu,
                device_identifier=int(instance.udsdatabasevalueentry_set.get(type__name='DTCDeviceIdentifier').value),
                failure_type=int(instance.udsdatabasevalueentry_set.get(type__name='DTCFailureType').value)
            )
            instance.save()
