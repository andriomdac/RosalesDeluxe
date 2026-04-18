from django.contrib import admin
from .models import Client, Employee, Vehicle, ServiceOrder, Service, EmployeeService, CashRegister, Payment, Outflow

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'commission')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'model_name', 'client')

class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1

@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'total_price', 'status', 'start_date')
    list_filter = ('status',)
    inlines = [ServiceInline]

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_order', 'price')

@admin.register(EmployeeService)
class EmployeeServiceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'service')

@admin.register(CashRegister)
class CashRegisterAdmin(admin.ModelAdmin):
    list_display = ('register_date', 'total_amount', 'is_open')
    list_filter = ('is_open', 'register_date')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('service_order', 'amount', 'payment_method', 'created_at')
    list_filter = ('payment_method', 'created_at')

@admin.register(Outflow)
class OutflowAdmin(admin.ModelAdmin):
    list_display = ('description', 'cash_register', 'amount', 'created_at')
    list_filter = ('cash_register', 'created_at')
