import dtc
import ecu
import report
import vehicle

from django.shortcuts import render
from reporter.models import VehicleSnapshot, Vehicle


def index(request):
    vehicle_count = Vehicle.objects.count()
    report_count = VehicleSnapshot.objects.count()
    return render(request, 'index.html', {
        'vehicle_count': vehicle_count,
        'report_count': report_count
    })