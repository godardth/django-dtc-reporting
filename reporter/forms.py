from django import forms
from reporter.models import VehicleSnapshot

class VehicleSnapshotForm(forms.ModelForm):
    class Meta:
        model = VehicleSnapshot
        fields = ['file', ]