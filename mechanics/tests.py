from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Mechanic, Service


class MechanicAPITests(APITestCase):
    def setUp(self):
        self.service = Service.objects.create(name="Oil Change")
        self.mechanic = Mechanic.objects.create(
            name="Ravi Kumar",
            phone="9876543210",
            location="Delhi",
            rating=4.5,
            is_open=True,
        )
        self.mechanic.services.add(self.service)

    def test_list_mechanics(self):
        url = reverse("mechanic-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_mechanic_by_id(self):
        url = reverse("mechanic-detail", args=[self.mechanic.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Ravi Kumar")

    def test_get_mechanic_not_found(self):
        url = reverse("mechanic-detail", args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_mechanic_success(self):
        url = reverse("mechanic-list")
        payload = {
            "name": "Suresh Auto",
            "phone": "9123456789",
            "location": "Mumbai",
            "rating": 4.0,
            "is_open": True,
            "services": ["Tyre Repair", "Battery Replacement"],
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["services"]), 2)

    def test_create_mechanic_invalid_phone(self):
        url = reverse("mechanic-list")
        payload = {
            "name": "Bad Phone Garage",
            "phone": "12345",
            "location": "Pune",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_mechanic(self):
        url = reverse("mechanic-detail", args=[self.mechanic.id])
        response = self.client.patch(url, {"rating": 5.0}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data["rating"]), 5.0)

    def test_delete_mechanic(self):
        url = reverse("mechanic-detail", args=[self.mechanic.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Mechanic.objects.filter(id=self.mechanic.id).exists())


class ServiceRequestAPITests(APITestCase):
    def setUp(self):
        self.service = Service.objects.create(name="Oil Change")
        self.mechanic = Mechanic.objects.create(
            name="Ravi Kumar",
            phone="9876543210",
            location="Delhi",
            rating=4.5,
            is_open=True,
        )
        self.mechanic.services.add(self.service)
        self.url = reverse("service-request-list")

    def valid_payload(self, **overrides):
        payload = {
            "customer_name": "Amit Sharma",
            "customer_phone": "9988776655",
            "vehicle_number": "KA01AB1234",
            "mechanic_id": self.mechanic.id,
            "service": "Oil Change",
            "problem_description": "Engine oil needs replacement.",
        }
        payload.update(overrides)
        return payload

    def test_create_service_request_success(self):
        response = self.client.post(self.url, self.valid_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "PENDING")

    def test_create_service_request_invalid_mechanic(self):
        response = self.client.post(
            self.url, self.valid_payload(mechanic_id=9999), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_service_request_invalid_phone(self):
        response = self.client.post(
            self.url, self.valid_payload(customer_phone="12345"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_service_request_invalid_vehicle_number(self):
        response = self.client.post(
            self.url, self.valid_payload(vehicle_number="XYZ"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_service_request_invalid_service(self):
        response = self.client.post(
            self.url, self.valid_payload(service="Engine Rebuild"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_service_request_missing_field(self):
        payload = self.valid_payload()
        del payload["customer_name"]
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)