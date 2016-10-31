from django.shortcuts import render
from reporter.models import Vehicle, DtcSnapshot


def dtcs(request):
    dtcs = DtcSnapshot.objects.distinct('device_identifier__value', 'failure_type__value')
    return render(request, 'dtcs.html', {'dtcs': dtcs})

 
def dtc(request, **kwargs):
    dtc = Vehicle.objects.all()
    return render(request, 'dtc.html', {'dtc': dtc})