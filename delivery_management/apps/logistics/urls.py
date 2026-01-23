from django.urls import path
from . import views

urlpatterns = [
    #---------------- DRIVERS ----------------
    path('', views.drivers, name='drivers'), 
    path('create-driver/', views.create_driver, name='create-driver'),  
    path('update-driver/<str:pk>/', views.update_driver, name='update-driver'),
    path('delete-driver/<str:pk>/', views.delete_driver, name='delete-driver'),
    path('export-drivers-csv/', views.export_drivers_csv, name='export-drivers-csv'),
#---------------- VEHICLES ----------------
    path('vehicles/', views.vehicles, name='vehicles'), 
    path('create-vehicle/', views.create_vehicle, name='create-vehicle'),
    path('update-vehicle/<str:pk>/', views.update_vehicle, name='update-vehicle'),
    path('delete-vehicle/<str:pk>/', views.delete_vehicle, name='delete-vehicle'),
    path('export-vehicles-csv/', views.export_vehicles_csv, name='export-vehicles-csv'),
#---------------- DESTINATIONS ----------------

    path('destinations/', views.destinations, name='destinations'), 
    path('create-destination/', views.create_destination, name='create-destination'),
    path('update-destination/<str:pk>/', views.update_destination, name='update-destination'),
    path('delete-destination/<str:pk>/', views.delete_destination, name='delete-destination'),
    path('export-destinations-csv/', views.export_destinations_csv, name='export-destinations-csv'),

#---------------- SERVICE TYPES ----------------


    path('service-types/', views.service_types, name='service-types'), 
    path('create-service-type/', views.create_service_type, name='create-service-type'),    
    path('update-service-type/<str:pk>/', views.update_service_type, name='update-service-type'),
    path('delete-service-type/<str:pk>/', views.delete_service_type, name='delete-service-type'),
    path('export-service-types-csv/', views.export_service_types_csv, name='export-service-types-csv'),


#---------------- ZONES ----------------
    path('zones/', views.zones, name='zones'), 
    path('create-zone/', views.create_zone, name='create-zone'),              
    path('update-zone/<str:pk>/', views.update_zone, name='update-zone'),
    path('delete-zone/<str:pk>/', views.delete_zone, name='delete-zone'),
    path('export-zones-csv/', views.export_zones_csv, name='export-zones-csv'), 

  
]