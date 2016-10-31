from django.shortcuts import render
from reporter.models import Vehicle, Dtc, VehicleSnapshot, EcuSnapshot


def dtcs(request):
    dtcs = Dtc.objects.all()
    return render(request, 'dtcs.html', {'dtcs': dtcs})

 
def dtc(request, **kwargs):
    dtc = Dtc.objects.get(pk=kwargs.get('id'))
    failure_reports = VehicleSnapshot.objects.distinct().filter(ecusnapshot__dtcsnapshot__dtc=dtc)
    vehicles = Vehicle.objects.distinct().filter(vehiclesnapshot__ecusnapshot__dtcsnapshot__dtc=dtc)
    return render(request, 'dtc.html', {
        'dtc': dtc,
        'failure_reports': failure_reports,
        'vehicles': vehicles
    })