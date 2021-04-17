from django.shortcuts import render,get_object_or_404
from rest_framework.parsers import JSONParser
from .models import Client
from .serializers import ClientSerializer
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
import io
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication

# Create your views here.
def index(request):
    return render(request,'index.html')

def applyloan(request):
    return render(request,'loanapply.html')

def NEW(request):
    return render(request,'NEW.html')


class ClientModelViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    authentication_classes  = [BasicAuthentication]
    permission_classes = [IsAuthenticated]





