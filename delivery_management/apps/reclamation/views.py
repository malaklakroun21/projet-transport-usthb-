from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Avg, Q
from django.db.models.functions import TruncMonth, ExtractMonth
from django.utils import timezone
from datetime import timedelta

from .models import Reclamation, ReclamationComment, ReclamationDocument, ReclamationTask
from .forms import (
    ReclamationForm, ReclamationStatusForm, ReclamationCommentForm,
    ReclamationDocumentForm, ReclamationTaskForm, ReclamationFilterForm
)
from apps.clients.models import Client


@login_required
def reclamation_list(request):
    """Liste des réclamations avec filtres et statistiques"""
    reclamations = Reclamation.objects.select_related('client', 'assigned_to', 'created_by')
    
    # Filtrage direct via GET
    status = request.GET.get('status')
    type_reclamation = request.GET.get('type_reclamation')
    priority = request.GET.get('priority')
    search = request.GET.get('search')
    
    if status:
        reclamations = reclamations.filter(status=status)
    if type_reclamation:
        reclamations = reclamations.filter(type_reclamation=type_reclamation)
    if priority:
        reclamations = reclamations.filter(priority=priority)
    if search:
        reclamations = reclamations.filter(
            Q(reference__icontains=search) |
            Q(description__icontains=search) |
            Q(client__name__icontains=search)
        )
    
    # Statistiques
    stats = {
        'en_cours': Reclamation.objects.filter(status='en_cours').count(),
        'resolues': Reclamation.objects.filter(status='resolue').count(),
        'annulees': Reclamation.objects.filter(status='annulee').count(),
        'total': Reclamation.objects.count(),
    }
    
    # Clients pour le modal de création
    clients = Client.objects.all()
    
    context = {
        'reclamations': reclamations,
        'stats': stats,
        'clients': clients,
    }
    return render(request, 'reclamation/reclamation_list.html', context)


@login_required
def reclamation_create(request):
    """Créer une nouvelle réclamation"""
    if request.method == 'POST':
        form = ReclamationForm(request.POST)
        if form.is_valid():
            reclamation = form.save(commit=False)
            reclamation.created_by = request.user
            reclamation.save()
            form.save_m2m()  # Sauvegarder les relations M2M (shipments)
            messages.success(request, f'Réclamation {reclamation.reference} créée avec succès.')
            return redirect('reclamation_detail', pk=reclamation.pk)
    else:
        form = ReclamationForm()
    
    return render(request, 'reclamation/reclamation_form.html', {
        'form': form,
        'title': 'Nouvelle réclamation'
    })


@login_required
def reclamation_detail(request, pk):
    """Détail d'une réclamation avec commentaires, documents et tâches"""
    reclamation = get_object_or_404(
        Reclamation.objects.prefetch_related('comments', 'documents', 'tasks', 'shipments'),
        pk=pk
    )
    
    # Formulaires
    comment_form = ReclamationCommentForm()
    document_form = ReclamationDocumentForm()
    task_form = ReclamationTaskForm()
    status_form = ReclamationStatusForm(instance=reclamation)
    
    # Traitement des formulaires
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_comment':
            comment_form = ReclamationCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.reclamation = reclamation
                comment.author = request.user
                comment.save()
                messages.success(request, 'Commentaire ajouté.')
                return redirect('reclamation_detail', pk=pk)
        
        elif action == 'add_document':
            document_form = ReclamationDocumentForm(request.POST, request.FILES)
            if document_form.is_valid():
                doc = document_form.save(commit=False)
                doc.reclamation = reclamation
                doc.uploaded_by = request.user
                doc.save()
                messages.success(request, 'Document ajouté.')
                return redirect('reclamation_detail', pk=pk)
        
        elif action == 'add_task':
            task_form = ReclamationTaskForm(request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.reclamation = reclamation
                task.save()
                messages.success(request, 'Tâche créée.')
                return redirect('reclamation_detail', pk=pk)
        
        elif action == 'update_status':
            status_form = ReclamationStatusForm(request.POST, instance=reclamation)
            if status_form.is_valid():
                rec = status_form.save(commit=False)
                if rec.status == 'resolue' and not rec.resolved_at:
                    rec.resolved_at = timezone.now()
                rec.save()
                messages.success(request, 'Statut mis à jour.')
                return redirect('reclamation_detail', pk=pk)
    
    context = {
        'reclamation': reclamation,
        'comment_form': comment_form,
        'document_form': document_form,
        'task_form': task_form,
        'status_form': status_form,
    }
    return render(request, 'reclamation/reclamation_detail.html', context)


@login_required
def reclamation_edit(request, pk):
    """Modifier une réclamation"""
    reclamation = get_object_or_404(Reclamation, pk=pk)
    
    if request.method == 'POST':
        form = ReclamationForm(request.POST, instance=reclamation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Réclamation mise à jour.')
            return redirect('reclamation_detail', pk=pk)
    else:
        form = ReclamationForm(instance=reclamation)
    
    return render(request, 'reclamation/reclamation_form.html', {
        'form': form,
        'reclamation': reclamation,
        'title': f'Modifier {reclamation.reference}'
    })


@login_required
def reclamation_update_status(request, pk):
    """Mise à jour rapide du statut (AJAX)"""
    if request.method == 'POST':
        reclamation = get_object_or_404(Reclamation, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(Reclamation.STATUS_CHOICES):
            reclamation.status = new_status
            if new_status == 'resolue':
                reclamation.resolved_at = timezone.now()
            reclamation.save()
            
            return JsonResponse({
                'success': True,
                'status': new_status,
                'status_display': reclamation.get_status_display()
            })
    
    return JsonResponse({'success': False})


@login_required
def task_update_status(request, pk):
    """Mise à jour du statut d'une tâche (AJAX)"""
    if request.method == 'POST':
        task = get_object_or_404(ReclamationTask, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(ReclamationTask.STATUS_CHOICES):
            task.status = new_status
            if new_status == 'terminee':
                task.completed_at = timezone.now()
            task.save()
            
            return JsonResponse({
                'success': True,
                'status': new_status,
                'status_display': task.get_status_display()
            })
    
    return JsonResponse({'success': False})


@login_required
def reclamation_stats(request):
    """Statistiques et rapports des réclamations"""
    # Période par défaut: 30 derniers jours
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Statistiques générales
    total = Reclamation.objects.count()
    en_cours = Reclamation.objects.filter(status='en_cours').count()
    resolues = Reclamation.objects.filter(status='resolue').count()
    annulees = Reclamation.objects.filter(status='annulee').count()
    
    # Réclamations par type
    by_type = list(Reclamation.objects.values('type_reclamation').annotate(
        count=Count('id')
    ).order_by('-count'))
    
    # Réclamations par priorité
    by_priority = list(Reclamation.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('-count'))
    
    # Réclamations par mois (derniers 6 mois)
    six_months_ago = end_date - timedelta(days=180)
    by_month = list(Reclamation.objects.filter(
        created_at__gte=six_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month'))
    
    # Délai moyen de résolution
    resolved_reclamations = Reclamation.objects.filter(
        status='resolue', 
        resolved_at__isnull=False
    )
    
    avg_resolution_time = None
    if resolved_reclamations.exists():
        total_days = 0
        count = 0
        for rec in resolved_reclamations:
            if rec.resolved_at and rec.created_at:
                delta = rec.resolved_at - rec.created_at
                total_days += delta.days
                count += 1
        if count > 0:
            avg_resolution_time = round(total_days / count, 1)
    
    # Motifs récurrents (top 5)
    top_motifs = Reclamation.objects.values('type_reclamation').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Réclamations récentes
    recent = Reclamation.objects.select_related('client').order_by('-created_at')[:5]
    
    context = {
        'total': total,
        'en_cours': en_cours,
        'resolues': resolues,
        'annulees': annulees,
        'by_type': by_type,
        'by_priority': by_priority,
        'by_month': by_month,
        'avg_resolution_time': avg_resolution_time,
        'top_motifs': top_motifs,
        'recent': recent,
        'type_choices': dict(Reclamation.TYPE_CHOICES),
        'priority_choices': dict(Reclamation.PRIORITY_CHOICES),
    }
    return render(request, 'reclamation/reclamation_stats.html', context)


def get_client_shipments(request):
    """API pour récupérer les expéditions d'un client (AJAX)"""
    client_id = request.GET.get('client_id')
    if client_id:
        shipments = Shipment.objects.filter(client_id=client_id).values(
            'id', 'tracking_number'
        )
        return JsonResponse(list(shipments), safe=False)
    return JsonResponse([], safe=False)

