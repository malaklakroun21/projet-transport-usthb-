from django.urls import path
from . import views

app_name = 'tour'

urlpatterns = [
    # Liste et journal
    path('', views.tour_list, name='list'),
    path('journal/', views.tour_journal, name='journal'),
    path('export/', views.export_tours_csv, name='export'),
    
    # CRUD
    path('create/', views.tour_create, name='create'),
    path('<int:pk>/', views.tour_detail, name='detail'),
    path('<int:pk>/update/', views.tour_update, name='update'),
    path('<int:pk>/delete/', views.tour_delete, name='delete'),
    
    # Actions sur tournée
    path('<int:pk>/start/', views.tour_start, name='start'),
    path('<int:pk>/complete/', views.tour_complete, name='complete'),
    
    # Gestion des expéditions
    path('<int:pk>/add-expedition/', views.add_expedition, name='add_expedition'),
    path('<int:pk>/remove-expedition/<int:expedition_pk>/', views.remove_expedition, name='remove_expedition'),
]
