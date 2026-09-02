import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.response import Response

from .models import Mechanic, ServiceRequest
from .serializers import MechanicSerializer, ServiceRequestSerializer

logger = logging.getLogger("mechanics")


class MechanicViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for mechanics.

    list:        GET    /api/mechanics/
    retrieve:    GET    /api/mechanics/{id}/
    create:      POST   /api/mechanics/
    update:      PUT    /api/mechanics/{id}/
    partial_update: PATCH /api/mechanics/{id}/
    destroy:     DELETE /api/mechanics/{id}/

    Supports:
      ?search=<name or location>
      ?is_open=true|false
      ?ordering=rating,-rating
    """

    queryset = Mechanic.objects.all().prefetch_related("services")
    serializer_class = MechanicSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_open", "location"]
    search_fields = ["name", "location"]
    ordering_fields = ["rating", "name", "created_at"]

    def create(self, request, *args, **kwargs):
        logger.info("Creating mechanic: %s", request.data.get("name"))
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        logger.info("Deleting mechanic id=%s name=%s", instance.id, instance.name)
        self.perform_destroy(instance)
        return Response(
            {"message": f"Mechanic '{instance.name}' deleted successfully."},
            status=status.HTTP_200_OK,
        )


class ServiceRequestViewSet(viewsets.ModelViewSet):
    """
    Create and manage service requests.

    list:        GET    /api/service-requests/
    retrieve:    GET    /api/service-requests/{id}/
    create:      POST   /api/service-requests/
    update:      PUT    /api/service-requests/{id}/
    partial_update: PATCH /api/service-requests/{id}/   (e.g. update status)
    destroy:     DELETE /api/service-requests/{id}/

    Supports:
      ?status=PENDING
      ?mechanic=<mechanic_id>
    """

    queryset = ServiceRequest.objects.select_related("mechanic", "service").all()
    serializer_class = ServiceRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "mechanic"]
    ordering_fields = ["created_at"]

    def create(self, request, *args, **kwargs):
        logger.info(
            "New service request from %s for mechanic_id=%s",
            request.data.get("customer_name"),
            request.data.get("mechanic_id"),
        )
        return super().create(request, *args, **kwargs)