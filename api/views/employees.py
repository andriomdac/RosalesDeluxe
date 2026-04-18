from rest_framework import viewsets
from ..models import Employee
from ..serializers import EmployeeSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para listar, criar, detalhar, atualizar e deletar funcionários.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
