from rest_framework import viewsets, mixins
from ..models import ServiceOrder
from ..serializers import ServiceOrderSerializer

class ServiceOrderViewSet(mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    """
    ViewSet para criar ordens de serviço.
    """
    queryset = ServiceOrder.objects.all()
    serializer_class = ServiceOrderSerializer
