from django.db import models
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError

class Tenant(models.Model):
    """
    Modelo de Tenant (Inquilino/Empresa).
    Representa uma estética automotiva individual no sistema multi-tenant.
    Serve como a raiz de isolamento de dados para quase todas as outras entidades.
    """
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    cnpj = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

class Client(models.Model):
    """
    Representa um cliente de uma estética específica.
    Relaciona-se com Tenant e possui múltiplos veículos.
    """
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='clients')
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tenant', 'name', 'phone'], name='unique_client_name_phone_tenant')
        ]

    def __str__(self):
        return self.name

class Employee(models.Model):
    """
    Representa um funcionário da estética.
    Relaciona-se com Tenant e participa de EmployeeService para cálculo de comissões.
    """
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    commission = models.DecimalField(max_digits=5, decimal_places=2, help_text="Commission percentage (e.g., 10.00)")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tenant', 'name', 'phone'], name='unique_employee_name_phone_tenant')
        ]

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    """
    Representa um veículo que pertence a um cliente.
    Relaciona-se com Client e Tenant. A placa deve ser única por Tenant.
    """
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='vehicles')
    client = models.ForeignKey('Client', on_delete=models.PROTECT, related_name='vehicles')
    model_name = models.CharField(max_length=100)
    license_plate = models.CharField(max_length=10)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['client', 'model_name'], name='unique_client_vehicle_model'),
            models.UniqueConstraint(fields=['tenant', 'license_plate'], name='unique_vehicle_plate_tenant')
        ]

    def clean(self):
        if self.client and self.client.tenant != self.tenant:
            raise ValidationError("O cliente deve pertencer ao mesmo Tenant do veículo.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.license_plate} - {self.model_name}"

class ServiceOrderStatus(models.Model):
    """
    Define os status possíveis para uma Ordem de Serviço (ex: Agendado, Concluído).
    Relaciona-se com Tenant, permitindo fluxos de trabalho personalizados.
    """
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='service_order_statuses')
    name = models.CharField(max_length=50)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tenant', 'name'], name='unique_service_order_status_tenant')
        ]

    def __str__(self):
        return self.name

class ServiceOrder(models.Model):
    """
    Entidade central do sistema que agrupa serviços aplicados a um veículo.
    Relaciona-se com Tenant, Vehicle, ServiceOrderStatus e CashRegister.
    O campo total_price é calculado automaticamente com base nos Serviços atrelados.
    """
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='service_orders')
    vehicle = models.ForeignKey('Vehicle', on_delete=models.PROTECT, related_name='service_orders', null=True)
    description = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.ForeignKey('ServiceOrderStatus', on_delete=models.PROTECT, related_name='service_orders', null=True)
    cash_register = models.ForeignKey('CashRegister', on_delete=models.PROTECT, related_name='service_orders', null=True)

    def clean(self):
        if self.vehicle and self.vehicle.tenant != self.tenant:
            raise ValidationError("O veículo deve pertencer ao mesmo Tenant da Ordem de Serviço.")
        if self.status and self.status.tenant != self.tenant:
            raise ValidationError("O status deve pertencer ao mesmo Tenant da Ordem de Serviço.")
        if self.cash_register and self.cash_register.tenant != self.tenant:
            raise ValidationError("O caixa deve pertencer ao mesmo Tenant da Ordem de Serviço.")

    def update_total_price(self):
        total = self.services.aggregate(total=Sum('price'))['total'] or Decimal('0')
        self.total_price = total
        ServiceOrder.objects.filter(id=self.id).update(total_price=self.total_price)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} - {self.status}"

class Service(models.Model):
    """
    Representa um item de serviço individual dentro de uma Ordem de Serviço (ex: Lavagem Simples).
    Relaciona-se com ServiceOrder e é vinculado a funcionários via EmployeeService.
    Modificações nesta entidade disparam o recálculo do total_price da Ordem de Serviço pai.
    """
    service_order = models.ForeignKey('ServiceOrder', on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.service_order.update_total_price()

    def delete(self, *args, **kwargs):
        service_order = self.service_order
        super().delete(*args, **kwargs)
        service_order.update_total_price()

    def __str__(self):
        return f"{self.name} (Order #{self.service_order.id})"

class EmployeeService(models.Model):
    """
    Tabela de ligação que associa funcionários aos serviços realizados.
    Essencial para o cálculo de comissões por serviço.
    """
    employee = models.ForeignKey('Employee', on_delete=models.PROTECT, related_name='performed_services')
    service = models.ForeignKey('Service', on_delete=models.PROTECT, related_name='employee_services')

    def clean(self):
        if self.employee.tenant != self.service.service_order.tenant:
            raise ValidationError("O funcionário deve pertencer ao mesmo Tenant da Ordem de Serviço.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} -> {self.service.name}"

class CashRegister(models.Model):
    """
    Representa o controle financeiro diário (Caixa).
    Relaciona-se com Tenant e agrupa pagamentos, entradas e saídas.
    O campo total_amount é calculado automaticamente (Pagamentos + Entradas - Saídas).
    """
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='cash_registers')
    register_date = models.DateField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_open = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tenant', 'register_date'], name='unique_cash_register_date_tenant')
        ]

    def update_total_amount(self):
        payments_total = self.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        inflows_total = self.inflows.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        outflows_total = self.outflows.aggregate(total=Sum('amount'))['total'] or Decimal('0')

        self.total_amount = payments_total + inflows_total - outflows_total
        CashRegister.objects.filter(id=self.id).update(total_amount=self.total_amount)

    def __str__(self):
        status_str = "Open" if self.is_open else "Closed"
        return f"Cash Register {self.id} - {status_str} ({self.register_date})"

class PaymentMethod(models.Model):
    """
    Define as formas de pagamento aceitas (ex: Pix, Cartão, Dinheiro).
    Relaciona-se com Tenant.
    """
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='payment_methods')
    name = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tenant', 'name'], name='unique_payment_method_tenant')
        ]

    def __str__(self):
        return self.name

class Payment(models.Model):
    """
    Registra um pagamento efetuado para uma Ordem de Serviço.
    Relaciona-se com ServiceOrder, CashRegister e PaymentMethod.
    Modificações nesta entidade disparam o recálculo do total_amount do Caixa vinculado.
    """
    service_order = models.ForeignKey('ServiceOrder', on_delete=models.PROTECT, related_name='payments')
    cash_register = models.ForeignKey('CashRegister', on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.ForeignKey('PaymentMethod', on_delete=models.PROTECT, related_name='payments')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.payment_method.tenant != self.service_order.tenant:
            raise ValidationError("O método de pagamento deve pertencer ao mesmo Tenant da Ordem de Serviço.")
        if self.cash_register.tenant != self.service_order.tenant:
            raise ValidationError("O caixa deve pertencer ao mesmo Tenant da Ordem de Serviço.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        self.cash_register.update_total_amount()

    def delete(self, *args, **kwargs):
        cash_register = self.cash_register
        super().delete(*args, **kwargs)
        cash_register.update_total_amount()

    def __str__(self):
        return f"{self.service_order} - {self.payment_method} - ${self.amount}"

class Inflow(models.Model):
    """
    Registra entradas de dinheiro no caixa (ex: aportes, correções).
    Relaciona-se com CashRegister.
    Modificações nesta entidade disparam o recálculo do total_amount do Caixa vinculado.
    """
    cash_register = models.ForeignKey('CashRegister', on_delete=models.PROTECT, related_name='inflows')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.cash_register.update_total_amount()

    def delete(self, *args, **kwargs):
        cash_register = self.cash_register
        super().delete(*args, **kwargs)
        cash_register.update_total_amount()

    def __str__(self):
        return f"Inflow: {self.description} - R${self.amount}"

class Outflow(models.Model):
    """
    Registra saídas de dinheiro do caixa (ex: compra de insumos, pagamentos avulsos).
    Relaciona-se com CashRegister.
    Modificações nesta entidade disparam o recálculo do total_amount do Caixa vinculado.
    """
    cash_register = models.ForeignKey('CashRegister', on_delete=models.PROTECT, related_name='outflows')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.cash_register.update_total_amount()

    def delete(self, *args, **kwargs):
        cash_register = self.cash_register
        super().delete(*args, **kwargs)
        cash_register.update_total_amount()

    def __str__(self):
        return f"Outflow: {self.description} - R${self.amount}"
