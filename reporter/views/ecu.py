from django.shortcuts import render
from reporter.models import Ecu

    
def ecus(request):
    ecus = Ecu.objects.all()
    return render(request, 'ecus.html', {'ecus': ecus})
    

def ecu(request, **kwargs):
    ecu = Ecu.objects.all()
    return render(request, 'ecu.html', {'ecu': ecu})