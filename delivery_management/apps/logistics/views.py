from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import HttpResponse
import csv

from .models import Shipment, Driver, Vehicule, Destination, TypeService, Zone
from .forms import ExpeditionForm, DriverForm, VehiculeForm, DestinationForm, TypeServiceForm, ZoneForm


# ================ EXPEDITIONS ================

def expedition_list(request):
    expeditions = Shipment.objects.all().order_by("-id")
    return render(request, "logistics/expedition_list.html", {"expeditions": expeditions})


def expedition_detail(request, pk):
    expedition = get_object_or_404(Shipment, pk=pk)
    return render(request, "logistics/expedition_detail.html", {"expedition": expedition})


def create_expedition(request):
    if request.method == "POST":
        form = ExpeditionForm(request.POST)
        if form.is_valid():
            expedition = form.save()
            return redirect("expedition_detail", pk=expedition.pk)
    else:
        form = ExpeditionForm()
    return render(request, "logistics/create_expedition.html", {"form": form})


def update_expedition(request, pk):
    expedition = get_object_or_404(Shipment, pk=pk)
    if request.method == "POST":
        form = ExpeditionForm(request.POST, instance=expedition)
        if form.is_valid():
            expedition = form.save()
            return redirect("expedition_detail", pk=expedition.pk)
    else:
        form = ExpeditionForm(instance=expedition)
    return render(request, "logistics/update_expedition.html", {"form": form, "expedition": expedition})


def delete_expedition(request, pk):
    expedition = get_object_or_404(Shipment, pk=pk)
    if request.method == "POST":
        expedition.delete()
        return redirect("expedition_list")
    return render(request, "logistics/delete_expedition.html", {"expedition": expedition})


# ================ DRIVERS ================

def drivers(request):
    query = request.GET.get('q')
    available = request.GET.get('available')
    drivers_qs = Driver.objects.exclude(pk__isnull=True)

    if query:
        drivers_qs = drivers_qs.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(license_number__icontains=query)
        )

    if available == 'YES':
        drivers_qs = drivers_qs.filter(available=True)
    elif available == 'NO':
        drivers_qs = drivers_qs.filter(available=False)

    context = {
        'drivers': drivers_qs,
        'query': query,
        'available': available or 'ALL'
    }
    return render(request, 'driver/driver.html', context)



def create_driver(request):
    form = DriverForm()
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('drivers')
    return render(request, 'driver/driver-form.html', {'form': form})


def update_driver(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    form = DriverForm(instance=driver)
    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            return redirect('drivers')
    return render(request, 'driver/driver-form.html', {'form': form})


def delete_driver(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        driver.delete()
        return redirect('drivers')
    return render(request, 'driver/driver-delete.html', {'driver': driver})


def export_drivers_csv(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="drivers.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(['Prénom', 'Nom', 'Téléphone', 'Permis', 'Disponible'])
    for d in Driver.objects.all():
        writer.writerow([
            d.first_name,
            d.last_name,
            d.phone,
            d.license_number,
            'Oui' if d.available else 'Non'
        ])
    return response


# ================ VEHICULES ================

def vehicules(request):
    query = request.GET.get('q')
    vehicules_qs = Vehicule.objects.all()
    if query:
        vehicules_qs = vehicules_qs.filter(
            Q(immatriculation__icontains=query) | Q(type__icontains=query)
        )
    return render(request, 'vehicle/vehicle.html', {'vehicules': vehicules_qs, 'query': query})


def create_vehicule(request):
    form = VehiculeForm()
    if request.method == 'POST':
        form = VehiculeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vehicules')
    return render(request, 'vehicle/vehicle-form.html', {'form': form})


def update_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    form = VehiculeForm(instance=vehicule)
    if request.method == 'POST':
        form = VehiculeForm(request.POST, instance=vehicule)
        if form.is_valid():
            form.save()
            return redirect('vehicules')
    return render(request, 'vehicle/vehicle-form.html', {'form': form})


def delete_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if request.method == 'POST':
        vehicule.delete()
        return redirect('vehicules')
    return render(request, 'vehicle/vehicle-delete.html', {'vehicule': vehicule})


def export_vehicules_csv(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="vehicules.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(['Immatriculation', 'Type'])
    for v in Vehicule.objects.all():
        writer.writerow([v.immatriculation, v.type])
    return response


# ================ DESTINATIONS ================

def destinations(request):
    query = request.GET.get('q')
    destinations_qs = Destination.objects.select_related('zone').all()

    if query:
        destinations_qs = destinations_qs.filter(
            Q(ville__icontains=query) |
            Q(pays__icontains=query) |
            Q(code_postal__icontains=query) |
            Q(zone__nom__icontains=query)
        )

    return render(request, 'destination/destination.html', {
        'destinations': destinations_qs,
        'query': query
    })


def create_destination(request):
    form = DestinationForm()
    if request.method == 'POST':
        form = DestinationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('destinations')
    return render(request, 'destination/destination-form.html', {'form': form})


def update_destination(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    form = DestinationForm(instance=destination)
    if request.method == 'POST':
        form = DestinationForm(request.POST, instance=destination)
        if form.is_valid():
            form.save()
            return redirect('destinations')
    return render(request, 'destination/destination-form.html', {'form': form})


def delete_destination(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        destination.delete()
        return redirect('destinations')
    return render(request, 'destination/destination-delete.html', {'destination': destination})


def export_destinations_csv(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="destinations.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(['Adresse', 'Ville', 'Pays', 'Code Postal', 'Zone'])
    for d in Destination.objects.all():
        zone_nom = d.zone.nom if d.zone else ''
        writer.writerow([d.adresse, d.ville, d.pays, d.code_postal, zone_nom])
    return response


# ================ TYPES DE SERVICE ================

def type_services(request):
    query = request.GET.get('q')
    services = TypeService.objects.all()

    if query:
        services = services.filter(nom__icontains=query)

    return render(request, 'type/type.html', {
        'services': services,
        'query': query
    })


def create_type_service(request):
    form = TypeServiceForm()
    if request.method == 'POST':
        form = TypeServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('type-services')
    return render(request, 'type/type-form.html', {'form': form})


def update_type_service(request, pk):
    service = get_object_or_404(TypeService, pk=pk)
    form = TypeServiceForm(instance=service)
    if request.method == 'POST':
        form = TypeServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('type-services')
    return render(request, 'type/type-form.html', {'form': form})


def delete_type_service(request, pk):
    service = get_object_or_404(TypeService, pk=pk)
    if request.method == 'POST':
        service.delete()
        return redirect('type-services')
    return render(request, 'type/type-delete.html', {'service': service})


def export_type_services_csv(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="type_services.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Tarif Poids', 'Tarif Volume'])
    for s in TypeService.objects.all():
        writer.writerow([s.nom, s.weight_rate, s.volume_rate])
    return response


# ================ ZONES ================

def zones(request):
    query = request.GET.get('q')
    zones_qs = Zone.objects.all()

    if query:
        zones_qs = zones_qs.filter(nom__icontains=query)

    return render(request, 'zone/zone.html', {
        'zones': zones_qs,
        'query': query
    })


def create_zone(request):
    form = ZoneForm()
    if request.method == 'POST':
        form = ZoneForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('zones')
    return render(request, 'zone/zone-form.html', {'form': form})


def update_zone(request, pk):
    zone = get_object_or_404(Zone, pk=pk)
    form = ZoneForm(instance=zone)
    if request.method == 'POST':
        form = ZoneForm(request.POST, instance=zone)
        if form.is_valid():
            form.save()
            return redirect('zones')
    return render(request, 'zone/zone-form.html', {'form': form})


def delete_zone(request, pk):
    zone = get_object_or_404(Zone, pk=pk)
    if request.method == 'POST':
        zone.delete()
        return redirect('zones')
    return render(request, 'zone/zone-delete.html', {'zone': zone})


def export_zones_csv(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="zones.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(['Zone', 'Prix de base'])
    for z in Zone.objects.all():
        writer.writerow([z.nom, z.base_price])
    return response
