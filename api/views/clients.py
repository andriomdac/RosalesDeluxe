from rest_framework import viewsets
from ..models import Client
from ..serializers import ClientSerializer

class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet para listar, criar, detalhar, atualizar e deletar clientes.
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer