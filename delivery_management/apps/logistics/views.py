from django.shortcuts import render, get_object_or_404, redirect
from .models import Shipment
from .forms import ExpeditionForm


# Create your views here.

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
            # TODO: adjust redirect name to your urls.py name if different
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
            # TODO: adjust redirect name to your urls.py name if different
            return redirect("expedition_detail", pk=expedition.pk)
    else:
        form = ExpeditionForm(instance=expedition)

    return render(
        request,
        "logistics/update_expedition.html",
        {"form": form, "expedition": expedition},
    )


def delete_expedition(request, pk):
    expedition = get_object_or_404(Shipment, pk=pk)

    # Verification: only delete on POST (prevents accidental deletes via URL)
    if request.method == "POST":
        expedition.delete()
        # TODO: adjust redirect name to your urls.py name if different
        return redirect("expedition_list")

    return render(request, "logistics/delete_expedition.html", {"expedition": expedition})
from django.shortcuts import render, redirect, get_object_or_404
from .models import Driver,Vehicle,Destination,ServiceType,Zone
from .forms import DriverForm,VehicleForm,DestinationForm,ServiceTypeForm,zoneForm
from django.db.models import Q
from django.http import HttpResponse
import csv

# ---------------- LIST + FILTER ----------------
def drivers(request):
    query = request.GET.get('q')
    available = request.GET.get('available')

    drivers = Driver.objects.all()

    if query:
        drivers = drivers.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(license_number__icontains=query)
        )

    if available == 'YES':
        drivers = drivers.filter(available=True)
    elif available == 'NO':
        drivers = drivers.filter(available=False)

    context = {
        'drivers': drivers,
        'query': query,
        'available': available or 'ALL'
    }
    return render(request, 'driver/driver.html', context)

# ---------------- CREATE ----------------
def create_driver(request):
    form = DriverForm()
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('drivers')
    return render(request, 'driver/driver-form.html', {'form': form})

# ---------------- UPDATE ----------------
def update_driver(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    form = DriverForm(instance=driver)
    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            return redirect('drivers')
    return render(request, 'driver/driver-form.html', {'form': form})

# ---------------- DELETE ----------------
def delete_driver(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        driver.delete()
        return redirect('drivers')
    return render(request, 'driver/driver-delete.html', {'driver': driver})

# ---------------- EXPORT CSV ----------------
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

# ---------------- VEHICLES ----------------

def vehicles(request):
    query = request.GET.get('q')
    vehicles = Vehicle.objects.all()
    if query:
        vehicles = vehicles.filter(Q(plate_number__icontains=query) | Q(vehicle_type__icontains=query))
    return render(request, 'vehicle/vehicle.html', {'vehicles': vehicles, 'query': query})

def create_vehicle(request):
    form = VehicleForm()
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vehicles')
    return render(request, 'vehicle/vehicle-form.html', {'form': form})

def update_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    form = VehicleForm(instance=vehicle)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            return redirect('vehicles')
    return render(request, 'vehicle/vehicle-form.html', {'form': form})

def delete_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        vehicle.delete()
        return redirect('vehicles')
    return render(request, 'vehicle/vehicle-delete.html', {'vehicle': vehicle})

def export_vehicles_csv(request):
    response = HttpResponse(content_type='text/csv', headers={'Content-Disposition': 'attachment; filename="vehicles.csv"'})
    writer = csv.writer(response)
    writer.writerow(['Plaque', 'Type', 'Capacité', 'Statut'])
    for v in Vehicle.objects.all():
        writer.writerow([v.plate_number, v.vehicle_type, v.capacity, v.status])
    return response

# ---------------- DESTINATIONS ----------------

def destinations(request):
    query = request.GET.get('q')

    destinations = Destination.objects.select_related('zone').all()

    if query:
        destinations = destinations.filter(
            Q(city__icontains=query) |
            Q(country__icontains=query) |
            Q(postal_code__icontains=query) |
            Q(zone__name__icontains=query)
        )

    return render(request, 'destination/destination.html', {
        'destinations': destinations,
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
    writer.writerow(['Ville', 'Pays', 'Code Postal', 'Zone'])

    for d in Destination.objects.all():
        writer.writerow([d.city, d.country, d.postal_code, d.zone.name])

    return response

# ---------------- SERVICE TYPES ----------------
def service_types(request):
    query = request.GET.get('q')
    services = ServiceType.objects.all()

    if query:
        services = services.filter(name__icontains=query)

    return render(request, 'type/type.html', {
        'services': services,
        'query': query
    })


def create_service_type(request):
    form = ServiceTypeForm()
    if request.method == 'POST':
        form = ServiceTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('service-types')
    return render(request, 'type/type-form.html', {'form': form})


def update_service_type(request, pk):
    service = get_object_or_404(ServiceType, pk=pk)
    form = ServiceTypeForm(instance=service)
    if request.method == 'POST':
        form = ServiceTypeForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('service-types')
    return render(request, 'type/type-form.html', {'form': form})


def delete_service_type(request, pk):
    service = get_object_or_404(ServiceType, pk=pk)
    if request.method == 'POST':
        service.delete()
        return redirect('service-types')
    return render(request, 'type/type-delete.html', {'service': service})
def export_service_types_csv(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="service_types.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Tarif Poids', 'Tarif Volume'])

    for s in ServiceType.objects.all():
        writer.writerow([s.name, s.weight_rate, s.volume_rate])

    return response


# ---------------- ZONES ----------------

def zones(request):
    query = request.GET.get('q')
    zones = Zone.objects.all()

    if query:
        zones = zones.filter(name__icontains=query)

    return render(request, 'zone/zone.html', {
        'zones': zones,
        'query': query
    })


def create_zone(request):
    form = zoneForm()
    if request.method == 'POST':
        form = zoneForm(request.POST)
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
        writer.writerow([z.name, z.base_price])

    return response
