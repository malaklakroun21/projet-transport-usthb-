from django.contrib import admin
from .models import Shipment 
from .models import Driver, Vehicle, Tour, ServiceType, Destination
# Register your models here.

@admin.register(Shipment)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'client', 'status', 'service_type', 'destination', 'tour', 'total_price', 'created_at')
    list_filter = ('status', 'service_type', 'created_at')
    search_fields = ('tracking_number', 'client__last_name', 'destination__city')

@admin.register(Driver)
class ChauffeurAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'phone')
    search_fields = ('last_name',)

@admin.register(Vehicle)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'vehicle_type')
    search_fields = ('plate_number',)

@admin.register(Tour)
class TourneeAdmin(admin.ModelAdmin):
    list_display = ('tour_date', 'driver', 'vehicle')
    list_filter = ('tour_date',)

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('city', 'country', 'postal_code')
    search_fields = ('city', 'country')

@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
