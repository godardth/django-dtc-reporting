from django.shortcuts import render
from reporter.models import Vehicle


def vehicles(request):
    vehicles = Vehicle.objects.all()
    return render(request, 'vehicles.html', {'vehicles': vehicles})
   
  
def vehicle(request, **kwargs):
    vehicle = Vehicle.objects.get(pk=kwargs.get('vin'))
    return render(request, 'vehicle.html', {'vehicle': vehicle})