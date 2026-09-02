from rest_framework import serializers

from .models import Mechanic, Service, ServiceRequest


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "name"]


class MechanicSerializer(serializers.ModelSerializer):
    services = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list,
        write_only=True,  
    )

    class Meta:
        model = Mechanic
        fields = [
            "id",
            "name",
            "phone",
            "location",
            "rating",
            "is_open",
            "services",
        ]

    def validate_phone(self, value):
        if not value.isdigit() or len(value) != 10 or value[0] not in "6789":
            raise serializers.ValidationError(
                "Invalid phone number. Must be a 10-digit number starting with 6-9."
            )
        return value

    def validate_rating(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("Rating must be between 0 and 5.")
        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["services"] = list(instance.services.values_list("name", flat=True))
        return rep

    def _sync_services(self, mechanic, service_names):
        service_objs = []
        for name in service_names:
            service_obj, _ = Service.objects.get_or_create(name=name.strip())
            service_objs.append(service_obj)
        mechanic.services.set(service_objs)

    def create(self, validated_data):
        service_names = validated_data.pop("services", [])
        mechanic = Mechanic.objects.create(**validated_data)
        self._sync_services(mechanic, service_names)
        return mechanic

    def update(self, instance, validated_data):
        service_names = validated_data.pop("services", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if service_names is not None:
            self._sync_services(instance, service_names)
        return instance


class ServiceRequestSerializer(serializers.ModelSerializer):
    mechanic_id = serializers.PrimaryKeyRelatedField(
        source="mechanic",
        queryset=Mechanic.objects.all(),
        error_messages={
            "does_not_exist": "Mechanic with the given ID does not exist.",
            "incorrect_type": "Invalid mechanic ID. Must be an integer.",
        },
    )
    service = serializers.CharField(max_length=100)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            "id",
            "customer_name",
            "customer_phone",
            "vehicle_number",
            "mechanic_id",
            "service",
            "problem_description",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def validate_customer_phone(self, value):
        if not value.isdigit() or len(value) != 10 or value[0] not in "6789":
            raise serializers.ValidationError(
                "Invalid phone number. Must be a 10-digit number starting with 6-9."
            )
        return value

    def validate_vehicle_number(self, value):
        import re

        cleaned = value.upper().replace(" ", "").replace("-", "")
        if not re.match(r"^[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{4}$", cleaned):
            raise serializers.ValidationError(
                "Invalid vehicle number. Expected a format like 'KA01AB1234'."
            )
        return cleaned

    def validate(self, attrs):
        mechanic = attrs.get("mechanic")
        service_name = attrs.get("service")

        if mechanic is not None and service_name:
            service_obj = mechanic.services.filter(name__iexact=service_name.strip()).first()
            if not service_obj:
                offered = ", ".join(mechanic.services.values_list("name", flat=True)) or "none"
                raise serializers.ValidationError(
                    {
                        "service": (
                            f"Invalid service. '{service_name}' is not offered by "
                            f"mechanic '{mechanic.name}'. Services offered: {offered}."
                        )
                    }
                )
            attrs["service"] = service_obj
        return attrs

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["mechanic_id"] = instance.mechanic_id
        rep["service"] = instance.service.name
        return rep