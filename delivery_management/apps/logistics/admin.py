from django.contrib import admin
from .models import Expedition 
from .models import Chauffeur, Vehicule, Tournee, TypeService, Destination
# Register your models here.

@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('numero_suivi', 'client', 'status', 'type_service', 'destination', 'tournee', 'montant_total', 'date_creation')
    list_filter = ('status', 'type_service', 'date_creation')
    search_fields = ('numero_suivi', 'client__nom', 'destination__ville')

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone')
    search_fields = ('nom',)

@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('immatriculation', 'type')
    search_fields = ('immatriculation',)

@admin.register(Tournee)
class TourneeAdmin(admin.ModelAdmin):
    list_display = ('date', 'chauffeur', 'vehicule')
    list_filter = ('date',)

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('ville', 'pays', 'code_postal')
    search_fields = ('ville', 'pays')

@admin.register(TypeService)
class TypeServiceAdmin(admin.ModelAdmin):
    list_display = ('nom',)
