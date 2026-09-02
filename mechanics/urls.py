from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MechanicViewSet, ServiceRequestViewSet

router = DefaultRouter()
router.register(r"mechanics", MechanicViewSet, basename="mechanic")
router.register(r"service-requests", ServiceRequestViewSet, basename="service-request")

urlpatterns = [
    path("", include(router.urls)),
]