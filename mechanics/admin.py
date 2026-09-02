from django.contrib import admin

from .models import Mechanic, Service, ServiceRequest


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


@admin.register(Mechanic)
class MechanicAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "phone", "location", "rating", "is_open"]
    list_filter = ["is_open", "location"]
    search_fields = ["name", "location"]
    filter_horizontal = ["services"]


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "customer_name",
        "mechanic",
        "service",
        "status",
        "created_at",
    ]
    list_filter = ["status"]
    search_fields = ["customer_name", "vehicle_number"]