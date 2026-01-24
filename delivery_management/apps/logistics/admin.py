from django.contrib import admin
from .models import Shipment, Driver, Vehicule, Tour, TypeService, Destination, Zone

# Register your models here.

@admin.register(Shipment)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'id_client', 'status', 'id_service_type', 'id_destination', 'id_tour', 'total_price', 'created_at')
    list_filter = ('status', 'id_service_type', 'created_at')
    search_fields = ('tracking_number',)

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone')
    search_fields = ('last_name',)

@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('immatriculation', 'type')
    search_fields = ('immatriculation',)

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('tour_date', 'id_driver', 'id_vehicle')
    list_filter = ('tour_date',)

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('nom', 'base_price')
    search_fields = ('nom',)

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('ville', 'pays', 'code_postal', 'zone')
    search_fields = ('ville', 'pays')
    list_filter = ('zone',)

@admin.register(TypeService)
class TypeServiceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'weight_rate', 'volume_rate')
