from django.shortcuts import render,get_object_or_404
from rest_framework.parsers import JSONParser
from .models import CustomerProfile, Loan
from .serializers import CustomerSerializer, LoanSerializer
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
import io
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from rest_framework.authentication import BasicAuthentication,SessionAuthentication,TokenAuthentication
from django.shortcuts import  render, redirect
from .forms import NewUserForm
from .forms import LoanInputForm
from django.contrib.auth import login
from django.contrib import messages
from rest_framework.filters import SearchFilter,OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
import requests

class CanEditLoanRequest(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method == "GET":
            return (
                request.user.is_admin() or
                request.user.is_agent or request.user.is_customer
                )
        elif request.method == "POST":
            return (request.user.is_agent or request.user.is_customer)

        return (
            request.user.is_agent or request.user.is_admin() or
            request.user.is_customer
        )

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if obj.status == "approved" and request.method in ["PUT", "PATCH"]:
            return False
        elif request.method in ["PUT", "PATCH"]:
            return request.user.is_agent
        elif request.method == "DELETE":
            return request.user.is_admin()


        return (
            request.user.is_agent or request.user.is_admin() or
            (obj.customer and obj.customer.user == request.user)
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method == "POST":
            return (request.user.is_agent or request.user.is_admin())

        return (request.user.is_agent or request.user.is_admin() or request.user.is_customer)

    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return request.user.is_admin()
        return request.user.is_agent or request.user.is_admin() or  (obj.user and obj.user == request.user)


def index(request):
    return render(request,'index.html')


def applyloan(request):
    return render(request,'loanapply.html')


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            #login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("/")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm
    return render(request=request, template_name="register.html", context={"register_form":form})




class CustomerModelViewSet(viewsets.ModelViewSet):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsOwnerOrAdmin, IsAuthenticated]
    filter_backends = [SearchFilter,DjangoFilterBackend,OrderingFilter]
    search_fields = ['city']
    filterset_fields = ['city','country']
    def get_queryset(self):
        """
        Show all customers to agent and show customer only their
        record
        """
        user = self.request.user
        queryset = super().get_queryset()
      
        if user.is_authenticated and (user.is_admin() or user.is_agent):
            return queryset

        return queryset.filter(user=user.id)

class LoanModelViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [CanEditLoanRequest, IsAuthenticated] 
     
    def get_queryset(self):
        """
        Show all loan-requests to agent and show customer only their
        own loan-requests
        """
        user = self.request.user
        queryset = super().get_queryset()

        if user.is_authenticated and (user.is_admin() or user.is_agent):
            return queryset

        return queryset.filter(customer__user=user.id)


def applyloanview(request):
    if request.method == 'POST':
        form = LoanInputForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, "Loan application successful." )
            return redirect("/")
        messages.error(request, "Unsuccessful application. Invalid information.")
    form = LoanInputForm
    return render(request=request, template_name="applyloan.html", context={"loan_form":form})


def actions(request):
    return render(request,'actions.html')



def userprofile(request):
    user = request.user
    
    return render(request,'userprofile.html',context={'user':user})

def viewprofiles(request):
    profiles = CustomerProfile.objects.all()
    
    return render(request, 'profiles.html', context={'profiles':profiles})


def loanrequests(request):
    if request.GET.get('customer'):
        loanrequests = Loan.objects.filter(customer=request.GET.get('customer'))
    else:
        loanrequests = Loan.objects.all()
    return render(request, 'loanreq.html', context={'loanrequests':loanrequests})