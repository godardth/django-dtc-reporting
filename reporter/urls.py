from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^failure-reports/(?P<id>[0-9]+)$', views.failure_report, name='failure-report'),
    url(r'^failure-reports/$', views.failure_reports, name='failure-reports'),
    url(r'^vehicles/(?P<vin>[0-9A-Z]+)$', views.vehicle, name='vehicle'),
    url(r'^vehicles/', views.vehicles, name='vehicles'),
    url(r'^ecus/(?P<id>[0-9]+)$', views.ecu, name='ecu'),
    url(r'^ecus/', views.ecus, name='ecus'),
    url(r'^dtcs/(?P<id>[0-9]+)$', views.dtc, name='dtc'),
    url(r'^dtcs/', views.dtcs, name='dtcs'),
]
