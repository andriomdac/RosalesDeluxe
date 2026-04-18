from rest_framework import viewsets, mixins
from ..models import CashRegister
from ..serializers import CashRegisterSerializer

class CashRegisterViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """
    ViewSet para listar, criar e detalhar caixas.
    Não permite atualização ou exclusão.
    """
    queryset = CashRegister.objects.all()
    serializer_class = CashRegisterSerializer
