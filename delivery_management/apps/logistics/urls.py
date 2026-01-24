from django.urls import path
from . import views

urlpatterns = [
    # ================ EXPEDITIONS ================
    path('expeditions/', views.expedition_list, name='expedition_list'),
    path('expeditions/create/', views.create_expedition, name='create_expedition'),
    path('expeditions/<int:pk>/', views.expedition_detail, name='expedition_detail'),
    path('expeditions/<int:pk>/update/', views.update_expedition, name='update_expedition'),
    path('expeditions/<int:pk>/delete/', views.delete_expedition, name='delete_expedition'),
    path('expeditions/<int:pk>/status/', views.update_expedition_status, name='update_expedition_status'),
    path('expeditions/<int:pk>/pdf/', views.expedition_pdf, name='expedition_pdf'),
    path('expeditions/export/', views.export_expeditions_csv, name='export_expeditions_csv'),
    path('tracking/', views.track_expedition, name='track_expedition'),
    path('api/calculate-price/', views.calculate_price_api, name='calculate_price_api'),

    # ================ DRIVERS ================
    path('', views.drivers, name='drivers'),
    path('create-driver/', views.create_driver, name='create-driver'),
    path('update-driver/<str:pk>/', views.update_driver, name='update-driver'),
    path('delete-driver/<str:pk>/', views.delete_driver, name='delete-driver'),
    path('export-drivers-csv/', views.export_drivers_csv, name='export-drivers-csv'),

    # ================ VEHICULES ================
    path('vehicules/', views.vehicules, name='vehicules'),
    path('create-vehicule/', views.create_vehicule, name='create-vehicule'),
    path('update-vehicule/<str:pk>/', views.update_vehicule, name='update-vehicule'),
    path('delete-vehicule/<str:pk>/', views.delete_vehicule, name='delete-vehicule'),
    path('export-vehicules-csv/', views.export_vehicules_csv, name='export-vehicules-csv'),

    # ================ DESTINATIONS ================
    path('destinations/', views.destinations, name='destinations'),
    path('create-destination/', views.create_destination, name='create-destination'),
    path('update-destination/<str:pk>/', views.update_destination, name='update-destination'),
    path('delete-destination/<str:pk>/', views.delete_destination, name='delete-destination'),
    path('export-destinations-csv/', views.export_destinations_csv, name='export-destinations-csv'),

    # ================ TYPES DE SERVICE ================
    path('type-services/', views.type_services, name='type-services'),
    path('create-type-service/', views.create_type_service, name='create-type-service'),
    path('update-type-service/<str:pk>/', views.update_type_service, name='update-type-service'),
    path('delete-type-service/<str:pk>/', views.delete_type_service, name='delete-type-service'),
    path('export-type-services-csv/', views.export_type_services_csv, name='export-type-services-csv'),

    # ================ ZONES ================
    path('zones/', views.zones, name='zones'),
    path('create-zone/', views.create_zone, name='create-zone'),
    path('update-zone/<str:pk>/', views.update_zone, name='update-zone'),
    path('delete-zone/<str:pk>/', views.delete_zone, name='delete-zone'),
    path('export-zones-csv/', views.export_zones_csv, name='export-zones-csv'),
]
