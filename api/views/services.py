from rest_framework import viewsets
from ..models import Service
from ..serializers import ServiceSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para listar, criar, detalhar, atualizar e deletar serviços.
    Permite vincular funcionários no momento da criação via campo 'employee_ids'.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
