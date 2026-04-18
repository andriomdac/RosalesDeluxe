from rest_framework import serializers
from django.db import transaction
from .models import (
    Tenant, Client, Employee, Vehicle, CashRegister, 
    ServiceOrder, Service, EmployeeService, Payment, Outflow,
    ServiceOrderStatus, PaymentMethod, Inflow
)

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class CashRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashRegister
        fields = '__all__'

class ServiceOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOrder
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Service
        fields = ['id', 'service_order', 'name', 'price', 'employee_ids']

    def create(self, validated_data):
        employee_ids = validated_data.pop('employee_ids', [])
        
        with transaction.atomic():
            service = Service.objects.create(**validated_data)
            for employee_id in employee_ids:
                # O método save() do EmployeeService chamará o clean(), 
                # garantindo a trava de segurança multi-tenant.
                EmployeeService.objects.create(service=service, employee_id=employee_id)
            
        return service

class EmployeeServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeService
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class InflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inflow
        fields = '__all__'

class OutflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outflow
        fields = '__all__'

class ServiceOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOrderStatus
        fields = '__all__'

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'