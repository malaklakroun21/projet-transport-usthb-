from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import get_template
from django.utils import timezone
import csv
import json

from .models import Shipment, ShipmentStatusHistory, Driver, Vehicule, Destination, TypeService, Zone
from .forms import ExpeditionForm, DriverForm, VehiculeForm, DestinationForm, TypeServiceForm, ZoneForm


# ================ EXPEDITIONS ================

def expedition_list(request):
    expeditions = Shipment.objects.all().order_by("-id")
    
    # Advanced filters
    search = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    client_filter = request.GET.get('client', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    destination_filter = request.GET.get('destination', '')
    
    if search:
        expeditions = expeditions.filter(
            Q(tracking_number__icontains=search) |
            Q(id_client__name__icontains=search) |
            Q(id_destination__ville__icontains=search) |
            Q(description__icontains=search)
        )
    
    if status_filter:
        expeditions = expeditions.filter(status=status_filter)
    
    if client_filter:
        expeditions = expeditions.filter(id_client_id=client_filter)
    
    if date_from:
        expeditions = expeditions.filter(created_at__date__gte=date_from)
    
    if date_to:
        expeditions = expeditions.filter(created_at__date__lte=date_to)
    
    if destination_filter:
        expeditions = expeditions.filter(id_destination__ville__icontains=destination_filter)
    
    # Stats for dashboard
    stats = {
        'total': Shipment.objects.count(),
        'registered': Shipment.objects.filter(status='REGISTERED').count(),
        'transit': Shipment.objects.filter(status='TRANSIT').count(),
        'sorting': Shipment.objects.filter(status='SORTING').count(),
        'out_for_delivery': Shipment.objects.filter(status='OUT_FOR_DELIVERY').count(),
        'delivered': Shipment.objects.filter(status='DELIVERED').count(),
        'failed': Shipment.objects.filter(status='FAILED').count(),
    }
    
    # Get unique clients and destinations for filter dropdowns
    from apps.clients.models import Client
    clients = Client.objects.all()
    destinations = Destination.objects.values_list('ville', flat=True).distinct()
    
    context = {
        "expeditions": expeditions,
        "stats": stats,
        "clients": clients,
        "destinations": destinations,
        "status_choices": Shipment.STATUS_CHOICES,
        "filters": {
            "search": search,
            "status": status_filter,
            "client": client_filter,
            "date_from": date_from,
            "date_to": date_to,
            "destination": destination_filter,
        }
    }
    return render(request, "logistics/expedition_list.html", context)


def expedition_detail(request, pk):
    expedition = get_object_or_404(Shipment, pk=pk)
    status_history = expedition.status_history.all().order_by('changed_at')
    next_statuses = expedition.get_next_statuses()
    
    context = {
        "expedition": expedition,
        "status_history": status_history,
        "next_statuses": next_statuses,
        "status_choices": dict(Shipment.STATUS_CHOICES),
        "progress": expedition.get_status_progress(),
    }
    return render(request, "logistics/expedition_detail.html", context)


def create_expedition(request):
    if request.method == "POST":
        form = ExpeditionForm(request.POST)
        if form.is_valid():
            expedition = form.save(commit=False)
            if request.user.is_authenticated:
                expedition.created_by = request.user
            expedition.save()
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


@require_POST
def update_expedition_status(request, pk):
    """AJAX endpoint for status updates"""
    expedition = get_object_or_404(Shipment, pk=pk)
    
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        notes = data.get('notes', '')
        location = data.get('location', '')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    
    if not new_status:
        return JsonResponse({'success': False, 'error': 'Status required'}, status=400)
    
    if not expedition.can_transition_to(new_status):
        return JsonResponse({
            'success': False, 
            'error': f'Transition de {expedition.status} vers {new_status} non autorisée'
        }, status=400)
    
    # Update status
    expedition.status = new_status
    expedition.save()
    
    # Update history entry with additional info
    history = ShipmentStatusHistory.objects.filter(
        shipment=expedition, 
        status=new_status
    ).order_by('-changed_at').first()
    
    if history:
        if notes:
            history.notes = notes
        if location:
            history.location = location
        if request.user.is_authenticated:
            history.changed_by = request.user
        history.save()
    
    return JsonResponse({
        'success': True,
        'new_status': new_status,
        'status_display': dict(Shipment.STATUS_CHOICES).get(new_status),
        'progress': expedition.get_status_progress(),
        'next_statuses': expedition.get_next_statuses(),
    })


def track_expedition(request):
    """Public tracking page"""
    tracking_number = request.GET.get('tracking', '').strip().upper()
    expedition = None
    status_history = None
    error = None
    
    if tracking_number:
        try:
            expedition = Shipment.objects.get(tracking_number__iexact=tracking_number)
            status_history = expedition.status_history.all().order_by('changed_at')
        except Shipment.DoesNotExist:
            error = "Aucune expédition trouvée avec ce numéro de suivi."
    
    context = {
        "tracking_number": tracking_number,
        "expedition": expedition,
        "status_history": status_history,
        "error": error,
        "progress": expedition.get_status_progress() if expedition else 0,
        "status_choices": dict(Shipment.STATUS_CHOICES) if expedition else {},
    }
    return render(request, "logistics/track_expedition.html", context)


def expedition_pdf(request, pk):
    """Generate PDF shipping slip"""
    expedition = get_object_or_404(Shipment, pk=pk)
    
    # Try to use weasyprint for PDF generation
    try:
        from weasyprint import HTML
        
        template = get_template('logistics/expedition_pdf.html')
        html_string = template.render({
            'expedition': expedition,
            'generated_at': timezone.now(),
        })
        
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="bon_expedition_{expedition.tracking_number}.pdf"'
        return response
    except ImportError:
        # Fallback: return HTML for printing
        return render(request, 'logistics/expedition_pdf.html', {
            'expedition': expedition,
            'generated_at': timezone.now(),
            'print_mode': True,
        })


def calculate_price_api(request):
    """API endpoint for real-time price calculation"""
    service_type_id = request.GET.get('service_type')
    destination_id = request.GET.get('destination')
    weight = request.GET.get('weight', 0)
    volume = request.GET.get('volume', 0)
    
    try:
        weight = float(weight) if weight else 0
        volume = float(volume) if volume else 0
    except ValueError:
        return JsonResponse({'price': 0, 'error': 'Invalid weight or volume'})
    
    base_price = 0
    weight_rate = 0
    volume_rate = 0
    
    if destination_id:
        try:
            destination = Destination.objects.get(pk=destination_id)
            if destination.zone:
                base_price = float(destination.zone.base_price or 0)
        except Destination.DoesNotExist:
            pass
    
    if service_type_id:
        try:
            service = TypeService.objects.get(pk=service_type_id)
            weight_rate = float(service.weight_rate or 0)
            volume_rate = float(service.volume_rate or 0)
        except TypeService.DoesNotExist:
            pass
    
    total = base_price + (weight * weight_rate) + (volume * volume_rate)
    
    return JsonResponse({
        'price': round(total, 2),
        'base_price': base_price,
        'weight_cost': round(weight * weight_rate, 2),
        'volume_cost': round(volume * volume_rate, 2),
    })


def export_expeditions_csv(request):
    """Export expeditions to CSV"""
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="expeditions.csv"'},
    )
    response.write('\ufeff')  # BOM for Excel UTF-8
    writer = csv.writer(response)
    writer.writerow([
        'N° Suivi', 'Client', 'Destination', 'Type Service', 
        'Poids (kg)', 'Volume (m³)', 'Statut', 'Prix Total',
        'Date Création', 'Livraison Estimée', 'Livraison Réelle'
    ])
    
    expeditions = Shipment.objects.select_related(
        'id_client', 'id_destination', 'id_service_type'
    ).all()
    
    for exp in expeditions:
        writer.writerow([
            exp.tracking_number,
            str(exp.id_client) if exp.id_client else '-',
            str(exp.id_destination) if exp.id_destination else '-',
            str(exp.id_service_type) if exp.id_service_type else '-',
            exp.weight or '-',
            exp.volume or '-',
            exp.get_status_display(),
            exp.total_price,
            exp.created_at.strftime('%d/%m/%Y %H:%M'),
            exp.estimated_delivery_date.strftime('%d/%m/%Y') if exp.estimated_delivery_date else '-',
            exp.reel_delivery_date.strftime('%d/%m/%Y') if exp.reel_delivery_date else '-',
        ])
    
    return response


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
