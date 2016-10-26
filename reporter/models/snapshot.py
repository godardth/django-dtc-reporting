from __future__ import unicode_literals
import json
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from reporter.models import Vehicle, Ecu, EcuRequest, UdsDatabaseObjectType, UdsDatabase, UdsDatabaseValueEntry
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
    
    def __str__(self):
        return str(self.vehicle) + ' - ' + str(self.captured_on)
    
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
                ecu_snapshot.raw=str(ecu_section)
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
    
    def __str__(self):
        return str(self.ecu)
        
    @receiver(pre_save, sender='reporter.EcuSnapshot')
    def parse_file(sender, instance, signal, **kwargs):
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
                dtc_snapshot.raw=str(dtc_section) + str(next(dtc_snaphots_iter))
                dtc_snapshot.save()

    
class DtcSnapshot(models.Model):
    # Related objects
    ecu_snapshot = models.ForeignKey('reporter.EcuSnapshot', on_delete=models.CASCADE)
    # Snapshot Data (DTC Level)
    snapshot_data = models.TextField(blank=True, null=True)
    
    raw = None
    
    class Meta:
        verbose_name = 'DTC Snapshot'
    
    def __str__(self):
        return str(self.ecu_snapshot.vehicle_snapshot.vehicle.vin) + ' - ' + str(self.ecu_snapshot)
    
    @receiver(post_save, sender='reporter.DtcSnapshot')
    def create_dtcsnapshot_snapshot(sender, instance, created, signal, **kwargs):    
        if created:
            soup = BeautifulSoup(instance.raw, "html5lib")
            summary_line_cells = soup.select('.DTCName > tbody > tr > td')
            UdsDatabaseValueEntry.objects.create(
                parent=instance,
                type=UdsDatabaseObjectType.objects.get(name='DTCDeviceIdentifier'),
                value=int(summary_line_cells[2].string[1:], 16)
            )
            summary_table = soup.select('.StatusDTC > tbody')[0]
            if summary_table:
                # Define dictionary displayed value to database object name
                display2db = {
                    'FailureType': 'DTCFailureType',
                    'FailureTypeCategory' : 'DTCFailureType.Category',
                    'B0_ DTCStatus.testFailed' : 'DTCStatus.testFailed',
                    'B3_ DTCStatus.confirmedDTC' : 'DTCStatus.confirmedDTC',
                    'B4_ DTCStatus.testNotCompletedSinceLastClear' : 'DTCStatus.testNotCompletedSinceLastClear',
                    'B5_ DTCStatus.testFailedSinceLastClear' : 'DTCStatus.testFailedSinceLastClear',
                    'B6_ DTCStatus.testNotCompletedThisMonitoringCycle' : 'DTCStatus.testNotCompletedThisMonitoringCycle',
                    'B7_ DTCStatus.warningIndicatorRequested' : 'DTCStatus.warningIndicatorRequested'
                }
                # Extract raw data from table
                data = dict()
                for line in summary_table.select('tr')[1:]:
                    try:
                        data[line.select('td:nth-of-type(1)')[0].string] = line.select('td:nth-of-type(2)')[0].string[:line.select('td:nth-of-type(2)')[0].string.index(' ')]
                    except:
                        data[line.select('td:nth-of-type(1)')[0].string] = line.select('td:nth-of-type(2)')[0].string
                # Write parsed values in the object properties
                for key, value in data.iteritems():
                    try:
                        UdsDatabaseValueEntry.objects.create(
                            parent=instance,
                            type=UdsDatabaseObjectType.objects.get(name=display2db[key]),
                            value=value
                        )
                    except KeyError:
                        pass
            # ... from body table
            extradata_table = soup.select('.FreezeF')[0]
            if extradata_table:
                header_line = extradata_table.select('tr:nth-of-type(2) > th')[0].string
                # Initialize the data object
                extradata = {
                    'record': header_line[header_line.index('Record : ')+9:header_line.index(' ?(')],
                    'data': []
                }
                # Fill with the parsed data
                for datablock in extradata_table.select('.FreezeF'):
                    extradata['data'].append({
                        'request': datablock.select('td')[1].string[1:],
                        'value': datablock.select('td')[3].string
                    })
                instance.snapshot_data = json.dumps(extradata)
