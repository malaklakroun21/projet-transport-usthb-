from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count, Max
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils import timezone
import csv

from .models import Tour, TourExpedition
from .forms import TourForm, TourCreateForm, TourCompleteForm, AddExpeditionForm
from apps.logistics.models import Shipment, Driver, Vehicule


@login_required
def tour_list(request):
    """Liste des tournées avec filtres et statistiques"""
    query = request.GET.get('q')
    status_filter = request.GET.get('status')
    tours_qs = Tour.objects.select_related('id_driver', 'id_vehicle').all()
    
    if query:
        tours_qs = tours_qs.filter(
            Q(id_driver__first_name__icontains=query) |
            Q(id_driver__last_name__icontains=query) |
            Q(id_vehicle__immatriculation__icontains=query) |
            Q(comments__icontains=query)
        )
    
    if status_filter and status_filter != 'ALL':
        tours_qs = tours_qs.filter(status=status_filter)
    
    # Statistiques globales
    stats = {
        'total': tours_qs.count(),
        'pending': tours_qs.filter(status='pending').count(),
        'in_progress': tours_qs.filter(status='in_progress').count(),
        'completed': tours_qs.filter(status='completed').count(),
        'total_km': tours_qs.aggregate(Sum('kilometers'))['kilometers__sum'] or 0,
        'total_fuel': tours_qs.aggregate(Sum('fuel_consumption'))['fuel_consumption__sum'] or 0,
    }
    
    # Formulaire de création rapide pour le popup
    create_form = TourCreateForm()
    
    context = {
        'tours': tours_qs,
        'query': query,
        'status_filter': status_filter or 'ALL',
        'stats': stats,
        'status_choices': Tour.STATUS_CHOICES,
        'create_form': create_form,
    }
    return render(request, 'tour/tour_list.html', context)


@login_required
def tour_detail(request, pk):
    """Détail d'une tournée avec ses expéditions"""
    tour = get_object_or_404(Tour, pk=pk)
    tour_expeditions = tour.tour_expeditions.select_related('expedition').all()
    
    # Formulaire d'ajout d'expédition
    add_form = AddExpeditionForm(tour=tour)
    
    context = {
        'tour': tour,
        'tour_expeditions': tour_expeditions,
        'add_form': add_form,
    }
    return render(request, 'tour/tour_detail.html', context)


@login_required
def tour_create(request):
    """Créer une nouvelle tournée (via popup ou page dédiée)"""
    if request.method == 'POST':
        form = TourCreateForm(request.POST)
        if form.is_valid():
            tour = form.save()
            messages.success(request, f'Tournée #{tour.id_tour} créée avec succès.')
            # Si requête AJAX, retourner JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'tour_id': tour.id_tour,
                    'message': f'Tournée #{tour.id_tour} créée avec succès.'
                })
            return redirect('tour:detail', pk=tour.pk)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
    else:
        form = TourCreateForm()
    
    context = {
        'form': form,
        'title': 'Nouvelle tournée',
    }
    return render(request, 'tour/tour_form.html', context)


@login_required
def tour_update(request, pk):
    """Modifier une tournée"""
    tour = get_object_or_404(Tour, pk=pk)
    
    if request.method == 'POST':
        form = TourForm(request.POST, instance=tour)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tournée #{tour.id_tour} modifiée avec succès.')
            return redirect('tour:detail', pk=tour.pk)
    else:
        form = TourForm(instance=tour)
    
    context = {
        'form': form,
        'tour': tour,
        'title': f'Modifier tournée #{tour.id_tour}',
    }
    return render(request, 'tour/tour_form.html', context)


@login_required
def tour_delete(request, pk):
    """Supprimer une tournée"""
    tour = get_object_or_404(Tour, pk=pk)
    
    if request.method == 'POST':
        tour_id = tour.id_tour
        # Remettre les expéditions en attente
        for te in tour.tour_expeditions.all():
            te.expedition.status = 'PENDING'
            te.expedition.save()
        tour.delete()
        messages.success(request, f'Tournée #{tour_id} supprimée.')
        return redirect('tour:list')
    
    return render(request, 'tour/tour_delete.html', {'tour': tour})


@login_required
def tour_start(request, pk):
    """Démarrer une tournée"""
    tour = get_object_or_404(Tour, pk=pk)
    
    if tour.status == 'pending':
        if not tour.id_driver or not tour.id_vehicle:
            messages.error(request, 'Veuillez assigner un chauffeur et un véhicule avant de démarrer.')
            return redirect('tour:detail', pk=pk)
        
        if tour.expedition_count == 0:
            messages.error(request, 'Veuillez ajouter au moins une expédition avant de démarrer.')
            return redirect('tour:detail', pk=pk)
        
        tour.status = 'in_progress'
        tour.starting_hour = timezone.now().time()
        tour.save()
        
        # Mettre les expéditions en transit
        for te in tour.tour_expeditions.all():
            te.expedition.status = 'IN_TRANSIT'
            te.expedition.save()
        
        messages.success(request, f'Tournée #{tour.id_tour} démarrée.')
    
    return redirect('tour:detail', pk=pk)


@login_required
def tour_complete(request, pk):
    """Terminer une tournée"""
    tour = get_object_or_404(Tour, pk=pk)
    
    if tour.status != 'in_progress':
        messages.error(request, 'Cette tournée ne peut pas être terminée.')
        return redirect('tour:detail', pk=pk)
    
    if request.method == 'POST':
        form = TourCompleteForm(request.POST)
        if form.is_valid():
            tour.status = 'completed'
            tour.finishing_hour = timezone.now().time()
            tour.kilometers = form.cleaned_data['kilometers']
            tour.fuel_consumption = form.cleaned_data.get('fuel_consumption') or 0
            tour.has_delay = form.cleaned_data.get('has_delay', False)
            tour.delay_minutes = form.cleaned_data.get('delay_minutes') or 0
            tour.has_technical_issue = form.cleaned_data.get('has_technical_issue', False)
            tour.technical_issue_description = form.cleaned_data.get('technical_issue_description', '')
            tour.comments = form.cleaned_data.get('comments', '')
            tour.save()
            
            # Marquer les expéditions comme livrées
            for te in tour.tour_expeditions.all():
                te.delivered = True
                te.delivered_at = timezone.now()
                te.save()
                te.expedition.status = 'DELIVERED'
                te.expedition.reel_delivery_date = timezone.now().date()
                te.expedition.save()
            
            messages.success(request, f'Tournée #{tour.id_tour} terminée avec succès.')
            return redirect('tour:detail', pk=pk)
    else:
        form = TourCompleteForm(initial={
            'kilometers': tour.kilometers,
            'fuel_consumption': tour.fuel_consumption,
        })
    
    return render(request, 'tour/tour_complete.html', {'tour': tour, 'form': form})


@login_required
def add_expedition(request, pk):
    """Ajouter une expédition à une tournée"""
    tour = get_object_or_404(Tour, pk=pk)
    
    if tour.status != 'pending':
        messages.error(request, 'Impossible de modifier une tournée en cours ou terminée.')
        return redirect('tour:detail', pk=pk)
    
    if request.method == 'POST':
        form = AddExpeditionForm(request.POST, tour=tour)
        if form.is_valid():
            expedition = form.cleaned_data['expedition']
            # Déterminer l'ordre
            max_order = tour.tour_expeditions.aggregate(max_order=Max('order'))['max_order'] or 0
            TourExpedition.objects.create(
                tour=tour,
                expedition=expedition,
                order=max_order + 1
            )
            expedition.status = 'PENDING'
            expedition.save()
            messages.success(request, f'Expédition {expedition.tracking_number} ajoutée.')
    
    return redirect('tour:detail', pk=pk)


@login_required
def remove_expedition(request, pk, expedition_pk):
    """Retirer une expédition d'une tournée"""
    tour = get_object_or_404(Tour, pk=pk)
    
    if tour.status != 'pending':
        messages.error(request, 'Impossible de modifier une tournée en cours ou terminée.')
        return redirect('tour:detail', pk=pk)
    
    tour_exp = get_object_or_404(TourExpedition, tour=tour, expedition_id=expedition_pk)
    expedition = tour_exp.expedition
    tour_exp.delete()
    
    expedition.status = 'CREATED'
    expedition.save()
    
    messages.success(request, f'Expédition {expedition.tracking_number} retirée.')
    return redirect('tour:detail', pk=pk)


@login_required
def tour_journal(request):
    """Journal des tournées - analyse des performances"""
    from datetime import timedelta
    
    period = request.GET.get('period', 'month')
    
    tours_qs = Tour.objects.filter(status='completed')
    
    if period == 'week':
        start_date = timezone.now().date() - timedelta(days=7)
        tours_qs = tours_qs.filter(tour_date__gte=start_date)
    elif period == 'month':
        start_date = timezone.now().date() - timedelta(days=30)
        tours_qs = tours_qs.filter(tour_date__gte=start_date)
    
    # Statistiques
    stats = tours_qs.aggregate(
        total_tours=Count('id_tour'),
        total_km=Sum('kilometers'),
        total_fuel=Sum('fuel_consumption'),
        delays_count=Count('id_tour', filter=Q(has_delay=True)),
        issues_count=Count('id_tour', filter=Q(has_technical_issue=True)),
    )
    
    # Expéditions livrées
    delivered_count = TourExpedition.objects.filter(
        tour__in=tours_qs,
        delivered=True
    ).count()
    
    stats['delivered_count'] = delivered_count
    stats['avg_km_per_tour'] = (stats['total_km'] or 0) / max(stats['total_tours'] or 1, 1)
    stats['avg_fuel_per_tour'] = (stats['total_fuel'] or 0) / max(stats['total_tours'] or 1, 1)
    
    context = {
        'tours': tours_qs.order_by('-tour_date')[:50],
        'stats': stats,
        'period': period,
    }
    return render(request, 'tour/tour_journal.html', context)


@login_required
def export_tours_csv(request):
    """Exporter les tournées en CSV"""
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="tournees.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(['ID', 'Date', 'Chauffeur', 'Véhicule', 'Statut', 'Km', 'Carburant', 'Expéditions', 'Retard', 'Problème technique'])
    
    for t in Tour.objects.all():
        driver = f"{t.id_driver}" if t.id_driver else ''
        vehicle = t.id_vehicle.immatriculation if t.id_vehicle else ''
        writer.writerow([
            t.id_tour, t.tour_date, driver, vehicle, t.get_status_display(),
            t.kilometers, t.fuel_consumption, t.expedition_count,
            'Oui' if t.has_delay else 'Non',
            'Oui' if t.has_technical_issue else 'Non'
        ])
    return response
