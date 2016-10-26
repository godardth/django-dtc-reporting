from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from reporter.forms import VehicleSnapshotForm
from reporter.models import VehicleSnapshot, Vehicle, Ecu, DtcSnapshot


def index(request):
    vehicle_count = Vehicle.objects.count()
    report_count = VehicleSnapshot.objects.count()
    return render(request, 'index.html', {
        'vehicle_count': vehicle_count,
        'report_count': report_count
    })

def failure_reports(request):
    if request.method == 'POST':
        form = VehicleSnapshotForm(request.POST, request.FILES)
        if form.is_valid():
            new_snapshot = VehicleSnapshot(file = request.FILES['file'])
            new_snapshot.save()
            return HttpResponseRedirect(reverse('failure-report', kwargs={'id': new_snapshot.pk}))
    else:
        form = VehicleSnapshotForm()
    reports = VehicleSnapshot.objects.all()
    return render(request, 'reports.html', {'reports': reports, 'form': form})
    
def failure_report(request, **kwargs):
    report = VehicleSnapshot.objects.get(pk=kwargs.get('id'))
    return render(request, 'report.html', {'report': report})
    
    
def vehicles(request):
    vehicles = Vehicle.objects.all()
    return render(request, 'vehicles.html', {'vehicles': vehicles})
    
def vehicle(request, **kwargs):
    vehicle = Vehicle.objects.get(pk=kwargs.get('vin'))
    return render(request, 'vehicle.html', {'vehicle': vehicle})
    
def ecus(request):
    ecus = Ecu.objects.all()
    return render(request, 'ecus.html', {'ecus': ecus})
    
def ecu(request, **kwargs):
    ecu = Ecu.objects.all()
    return render(request, 'ecu.html', {'ecu': ecu})
    
def dtcs(request):
    dtcs = DtcSnapshot.objects.distinct('device_identifier__value', 'failure_type__value')
    return render(request, 'dtcs.html', {'dtcs': dtcs})
    
def dtc(request, **kwargs):
    dtc = Vehicle.objects.all()
    return render(request, 'dtc.html', {'dtc': dtc})