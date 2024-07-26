from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
from app.utils import BaseViewSet
from django.conf import settings
from .models import *
from .serializers import *
import requests, logging, json

logger = logging.getLogger(__name__)

# Create your views here.
class AllVulnerabilities(viewsets.ModelViewSet):

    queryset = Vulnerabilities.objects.all()
    serializer_class = VulnerabilitiesSerializer


    def create(self, request):
        """
        Se personaliza método para el guardado de vulnerabilidades fixeadas
        """
        serializer = VulnerabilitiesSerializer(data=request.data)
        
        if serializer.is_valid():
            if (self.search_vulnerabiltie(serializer.validated_data.get('cve_id'))['status'] == True):
                serializer.save()
                return Response({'status': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'status': False, 'error': "cve_id don't exists in NIST list"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['GET'], url_path='all')
    def vulnerabilities(self, request):
        """
        Método encargado de obtener todas las vulnerabilidades, con o sin las fixeadas
        """
        try:
            new_serializer = VulnerabilitiesPagSerializer(data=request.query_params)
            if new_serializer.is_valid():

                params = {"resultsPerPage": new_serializer.data.get('page_size'),
                          "startIndex": new_serializer.data.get('index')}
                response = requests.request("GET",settings.URL_NIST, params=params, timeout=10)
                filter_list = []
                new_list = []
                if response.status_code == requests.codes.ok:
                    data = json.loads(response.text)
                    if request.GET.get('filter_fixed') == 'True':
                        data_vulnerabilities = Vulnerabilities.objects.all()
                        for i in data_vulnerabilities.values():
                            filter_list.append(i['cve_id'])
                        for j in data['vulnerabilities']:
                            if j['cve']['id'] not in filter_list:
                                new_list.append(j)
                        data['vulnerabilities'] = new_list
                        return Response({'status': True, 'data': data}, status=status.HTTP_200_OK)
                    return Response({'status': True, 'data': data}, status=status.HTTP_200_OK)
                return Response({'status': False, 'error': 'bad requests for API Nist'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'status': False, 'error': new_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    @action(detail=False, methods=['GET'], url_path='summarized')
    def summarized(self, request):
        """
        Método encargado de sumarizar las vulnerabilidades por severidad
        """
        try:
            severity = ["MEDIUM", "LOW", "HIGH", "CRITICAL"]
            data = {}
            for item in severity:
                response = requests.request("GET",settings.URL_NIST, params={"cvssV3Severity": item}, timeout=10)

                if response.status_code == requests.codes.ok:
                    all_data = json.loads(response.text)
                    data[item] = all_data['totalResults']
            if (data['MEDIUM'] and data['LOW'] and data['HIGH']):
                data['TOTAL'] = data['MEDIUM'] + data['LOW'] + data['HIGH']
            return Response({'status': True, 'data': data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def search_vulnerabiltie(self, ids):
        """
        Función encargada de validar si la vulnerabilidad a guardar en la App existe en el NIST
        """
        try:
            response = requests.request("GET", settings.URL_NIST, params={"cveId": ids}, timeout=10)
            if response.status_code == requests.codes.ok:
                data = json.loads(response.text)
                if data['totalResults'] > 0:
                    return {'status': True}
                else:
                    return {'status': False}
            return {'status': False, 'error': 'error service NIST'}
        except Exception as e:
            return {'status': False, 'error': str(e)}
        


class AdminUsersViewSet(BaseViewSet):
    '''
    Vista para el modelo de usuarios
    '''
    queryset = User.objects.all().prefetch_related(
            "groups",
            "user_permissions"
        ).order_by('-id')
    serializer_class = UserSerializer
    ordering_fields = ('username', 'first_name', 'is_active', 'last_name', 'email', 'surname', 'document')

    
    def create(self, request):
        """
        Método encargado de la creación de usuarios
        """
        instance = self.queryset.filter(
            username=request.data.get("username", None)
        ).exists()
        if instance:
            return Response({"username": ["El usuario ya existe."]}, status=400)
        self.serializer_class = SaveUserSerializer
        return super().create(request)
    
    def update(self, request, pk=None):
        """
        Método encargado de la actualización de usuarios
        """
        self.serializer_class = SaveUserSerializer
        return super().update(request, pk)