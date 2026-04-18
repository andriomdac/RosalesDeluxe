from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.clients import ClientViewSet
from .views.employees import EmployeeViewSet
from .views.vehicles import VehicleViewSet
from .views.cash_registers import CashRegisterViewSet
from .views.service_orders import ServiceOrderViewSet
from .views.services import ServiceViewSet

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'cash-registers', CashRegisterViewSet, basename='cash-register')
router.register(r'service-orders', ServiceOrderViewSet, basename='service-order')
router.register(r'services', ServiceViewSet, basename='service')

urlpatterns = [
    path('', include(router.urls)),
]
