from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Shipment, ShipmentStatusHistory, Tour


# Store the old status before save
@receiver(pre_save, sender=Shipment)
def store_old_status(sender, instance, **kwargs):
    """Store the old status to compare after save"""
    if instance.pk:
        try:
            old_instance = Shipment.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Shipment.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Shipment)
def create_status_history(sender, instance, created, **kwargs):
    """Create a status history entry when status changes"""
    if created:
        # New shipment - create initial history
        ShipmentStatusHistory.objects.create(
            shipment=instance,
            status=instance.status,
            notes="Expédition créée"
        )
    else:
        # Check if status changed
        old_status = getattr(instance, '_old_status', None)
        if old_status and old_status != instance.status:
            # Status changed - create history entry
            status_notes = {
                'REGISTERED': 'Expédition enregistrée',
                'TRANSIT': 'Colis pris en charge par le transporteur',
                'SORTING': 'Colis arrivé au centre de tri',
                'OUT_FOR_DELIVERY': 'Colis en cours de livraison',
                'DELIVERED': 'Colis livré avec succès',
                'FAILED': 'Échec de livraison',
            }
            ShipmentStatusHistory.objects.create(
                shipment=instance,
                status=instance.status,
                notes=status_notes.get(instance.status, '')
            )
            
            # Auto-update delivery date when delivered
            if instance.status == 'DELIVERED' and not instance.reel_delivery_date:
                Shipment.objects.filter(pk=instance.pk).update(
                    reel_delivery_date=timezone.now().date()
                )


@receiver(post_save, sender=Tour)
def update_shipments_on_tour_start(sender, instance, **kwargs):
    """When a tour starts, update related shipments to TRANSIT"""
    if instance.status == 'in_progress':
        # Get all shipments in this tour that are still REGISTERED
        shipments = Shipment.objects.filter(
            id_tour=instance,
            status='REGISTERED'
        )
        for shipment in shipments:
            shipment.status = 'TRANSIT'
            shipment.save()


@receiver(post_save, sender=Tour)
def update_shipments_on_tour_complete(sender, instance, **kwargs):
    """When tour completes, check for undelivered packages"""
    if instance.status == 'completed':
        # Shipments still in transit should move to sorting
        shipments = Shipment.objects.filter(
            id_tour=instance,
            status='TRANSIT'
        )
        for shipment in shipments:
            shipment.status = 'SORTING'
            shipment.save()
