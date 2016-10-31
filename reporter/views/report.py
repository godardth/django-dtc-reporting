from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from reporter.forms import VehicleSnapshotForm
from reporter.models import VehicleSnapshot, Vehicle, Ecu, DtcSnapshot


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