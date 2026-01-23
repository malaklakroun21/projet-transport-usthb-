from django.urls import path
from . import views

app_name = 'expedition'

urlpatterns = [
    path('nouveau/', views.expedition_wizard, name='wizard'),
    path('calculer-prix/', views.calculate_price_ajax, name='calculate_price'),
    path('success/<int:pk>/', views.expedition_success, name='success'),
    path('reset/', views.expedition_reset, name='reset'),
]
