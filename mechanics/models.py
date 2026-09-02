from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r"^[6-9]\d{9}$",
    message="Phone number must be a valid 10-digit Indian mobile number.",
)

vehicle_number_validator = RegexValidator(
    regex=r"^[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{4}$",
    message="Vehicle number must look like 'KA01AB1234'.",
)


class Service(models.Model):
    """Lookup table of service types a mechanic can offer (e.g. Oil Change, Tyre Repair)."""

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Mechanic(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=10, validators=[phone_validator])
    location = models.CharField(max_length=255)
    rating = models.DecimalField(
        max_digits=3, decimal_places=1, default=0.0
    )  # e.g. 4.5
    is_open = models.BooleanField(default=True)
    services = models.ManyToManyField(Service, related_name="mechanics", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class ServiceRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=10, validators=[phone_validator])
    vehicle_number = models.CharField(max_length=15, validators=[vehicle_number_validator])

    mechanic = models.ForeignKey(
        Mechanic, on_delete=models.CASCADE, related_name="service_requests"
    )
    service = models.ForeignKey(
        Service, on_delete=models.PROTECT, related_name="requests"
    )
    problem_description = models.TextField()

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Request #{self.id} - {self.customer_name} -> {self.mechanic.name}"