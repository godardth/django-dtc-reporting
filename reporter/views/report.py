from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.template import loader
from reporter.forms import VehicleSnapshotForm
from reporter.models import VehicleSnapshot, Vehicle, Ecu, DtcSnapshot
from django.core.exceptions import ValidationError

def failure_reports(request):
    # POST
    if request.method == 'POST':
        form = VehicleSnapshotForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                new_snapshot = VehicleSnapshot(file = request.FILES['file'])
                new_snapshot.save()
                return JsonResponse({'success': '200'})
            # Exception management
            except ValidationError as e:
                try:
                    if e.error_dict.get('vin', None):
                        return HttpResponseBadRequest(e.error_dict['vin'][0].message)
                except:
                    pass
                return HttpResponseBadRequest(e.message)
            except IndexError:
                return HttpResponseBadRequest('File invalid (index out of range)')
        else:
            return HttpResponseBadRequest()
    # GET
    else:
        form = VehicleSnapshotForm()
        reports = VehicleSnapshot.objects.all()
        return render(request, 'reports.html', {'reports': reports, 'form': form})


def failure_report(request, **kwargs):
    report = VehicleSnapshot.objects.get(pk=kwargs.get('id'))
    return render(request, 'report.html', {'report': report})


def failure_report_deletion(request, **kwargs):
    VehicleSnapshot.objects.get(pk=kwargs.get('id')).delete()
    return HttpResponseRedirect(reverse('failure-reports'))
