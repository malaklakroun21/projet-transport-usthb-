from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q

from .models import Incident, IncidentDocument, IncidentComment
from .forms import IncidentForm, IncidentStatusForm, IncidentDocumentForm, IncidentCommentForm
from apps.logistics.models import Shipment


@login_required
def incident_list(request):
    """Liste des incidents avec filtres"""
    incidents = Incident.objects.all()
    
    # Filtres
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    
    if status_filter:
        incidents = incidents.filter(status=status_filter)
    if type_filter:
        incidents = incidents.filter(incident_type=type_filter)
    
    # Statistiques
    stats = {
        'ouverts': Incident.objects.filter(status='ouvert').count(),
        'en_cours': Incident.objects.filter(status='en_cours').count(),
        'resolus': Incident.objects.filter(status='resolu').count(),
    }
    
    # Expéditions pour le modal de création
    shipments = Shipment.objects.all()
    
    context = {
        'incidents': incidents,
        'stats': stats,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'type_choices': Incident.TYPE_CHOICES,
        'status_choices': Incident.STATUS_CHOICES,
        'shipments': shipments,
    }
    return render(request, 'incidents/incident_list.html', context)


@login_required
def incident_create(request):
    """Créer un nouvel incident"""
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reported_by = request.user
            incident.save()
            messages.success(request, 'Incident créé avec succès.')
            return redirect('incident_detail', pk=incident.pk)
    else:
        form = IncidentForm()
    
    return render(request, 'incidents/incident_form.html', {
        'form': form,
        'title': 'Déclarer un incident'
    })


@login_required
def incident_detail(request, pk):
    """Détail d'un incident"""
    incident = get_object_or_404(Incident, pk=pk)
    comments = incident.comments.all()
    documents = incident.documents.all()
    
    # Formulaires
    comment_form = IncidentCommentForm()
    document_form = IncidentDocumentForm()
    status_form = IncidentStatusForm(instance=incident)
    
    if request.method == 'POST':
        if 'add_comment' in request.POST:
            comment_form = IncidentCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.incident = incident
                comment.author = request.user
                comment.save()
                messages.success(request, 'Commentaire ajouté.')
                return redirect('incident_detail', pk=pk)
        
        elif 'add_document' in request.POST:
            document_form = IncidentDocumentForm(request.POST, request.FILES)
            if document_form.is_valid():
                document = document_form.save(commit=False)
                document.incident = incident
                document.save()
                messages.success(request, 'Document ajouté.')
                return redirect('incident_detail', pk=pk)
        
        elif 'update_status' in request.POST:
            status_form = IncidentStatusForm(request.POST, instance=incident)
            if status_form.is_valid():
                incident = status_form.save(commit=False)
                if incident.status == 'resolu' and not incident.resolved_at:
                    incident.resolved_at = timezone.now()
                incident.save()
                messages.success(request, 'Statut mis à jour.')
                return redirect('incident_detail', pk=pk)
    
    context = {
        'incident': incident,
        'comments': comments,
        'documents': documents,
        'comment_form': comment_form,
        'document_form': document_form,
        'status_form': status_form,
    }
    return render(request, 'incidents/incident_detail.html', context)


@login_required
def incident_update_status(request, pk):
    """Mise à jour rapide du statut (AJAX)"""
    if request.method == 'POST':
        incident = get_object_or_404(Incident, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(Incident.STATUS_CHOICES):
            incident.status = new_status
            if new_status == 'resolu':
                incident.resolved_at = timezone.now()
            incident.save()
            return JsonResponse({'success': True, 'status': new_status})
        
        return JsonResponse({'success': False, 'error': 'Statut invalide'})
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})
