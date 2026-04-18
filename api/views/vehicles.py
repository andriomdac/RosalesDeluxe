from rest_framework import viewsets
from ..models import Vehicle
from ..serializers import VehicleSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para listar, criar, detalhar, atualizar e deletar veículos.
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
