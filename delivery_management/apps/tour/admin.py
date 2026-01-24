from django.contrib import admin
from .models import Tour, TourExpedition


class TourExpeditionInline(admin.TabularInline):
    model = TourExpedition
    extra = 0
    raw_id_fields = ['expedition']


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ['id_tour', 'tour_date', 'id_driver', 'id_vehicle', 'status', 'expedition_count', 'kilometers']
    list_filter = ['status', 'tour_date', 'has_delay', 'has_technical_issue']
    search_fields = ['id_driver__first_name', 'id_driver__last_name', 'id_vehicle__immatriculation']
    date_hierarchy = 'tour_date'
    inlines = [TourExpeditionInline]


@admin.register(TourExpedition)
class TourExpeditionAdmin(admin.ModelAdmin):
    list_display = ['tour', 'expedition', 'order', 'delivered', 'delivered_at']
    list_filter = ['delivered', 'tour__status']
    raw_id_fields = ['tour', 'expedition']
