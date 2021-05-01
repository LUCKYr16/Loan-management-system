import json
from django.conf import settings
from django.shortcuts import render,get_object_or_404
from rest_framework.parsers import JSONParser
from .models import CustomerProfile, Loan
from .serializers import CustomerSerializer, LoanSerializer, CustomerLoanSerializer
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
import io
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import  render, redirect
from .forms import NewUserForm
from django.contrib.auth import login
from django.contrib import messages
from rest_framework.filters import SearchFilter,OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from django.contrib.auth.decorators import login_required
from rest_framework.reverse import reverse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied



#Custome permissions for change in loan requests as well as for objects
class CanEditLoanRequest(permissions.BasePermission):
    # Function overriding

    # User must be authenticated
    # Only agent and customer can make a post request 
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        elif request.method == "POST":
            return (request.user.is_agent or request.user.is_customer)

        return (
            request.user.is_agent or request.user.is_admin() or
            request.user.is_customer
        )
    
    # Loan request cannot be edited after it is approved
    # Only admin can make a delete request
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.is_customer and obj.customer.user and \
                obj.customer.user != request.user:
            return False

        if obj.status == "approved" and request.method in ["PUT", "PATCH"]:
            return False
        elif request.method in ["PUT", "PATCH"]:
            return request.user.is_agent
        elif request.method == "DELETE":
            return request.user.is_admin()

        return (
            request.user.is_agent or request.user.is_admin() or
            request.user.is_customer
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method == "POST":
            return (request.user.is_agent or request.user.is_admin())

        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_customer and request.method in ["PUT", "PATCH"]:
            return False
        if request.method == "DELETE":
            return request.user.is_admin()
        return True


def index(request):
    return render(request,'index.html')


#Registration/signup
def register_request(request):
    errors = []
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful." )
            return redirect(reverse("login"))
        for k, v in json.loads(form.errors.as_json()).items():
            for error in v:
                errors.append("%s: %s" % (k, error.get("message")))

    form = NewUserForm
    return render(
        request=request, template_name="register.html",
        context={"register_form":form, "errors": errors}
    )


#Customer profiles view set
class CustomerModelViewSet(viewsets.ModelViewSet):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsOwnerOrAdmin, IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    search_fields = ['city']
    filterset_fields = ['city','country']
    renderer_classes = [TemplateHTMLRenderer] 




    @action(methods=["GET", "POST"], detail=True, permission_classes=[IsOwnerOrAdmin, IsAuthenticated])
    def edit(self, request, pk):
        """
        Renders form to edit customers
        """
        if request.method == "POST":
            customer = get_object_or_404(CustomerProfile, pk=pk)
            if request.user.is_agent or request.user.is_admin():
                return self.update(request, pk)
            else:
                raise PermissionDenied()
        customer = get_object_or_404(CustomerProfile, pk=pk)
        return Response(
            {'serializer': CustomerSerializer(customer), "customer": pk},
            template_name='edit_profile.html'
        )

    def update(self, request, pk=None):
        super(self.__class__, self).update(request, pk)
        customer =  get_object_or_404(CustomerProfile, pk=pk)
        return Response(
            {"customer": customer}, template_name='userprofile.html'
        )

    def list(self, request):
        queryset = self.get_queryset()

        return Response(
            {"customers": queryset}, template_name='customers.html'
        )

    def retrieve(self, request, pk=None):
        super(self.__class__, self).retrieve(request, pk)
        customer =  get_object_or_404(CustomerProfile, pk=pk)

        return Response(
            {"customer": customer},
            template_name='userprofile.html'
        )

    def get_queryset(self):
        """
        Show all customers to agent and show customer only their
        record
        """
        queryset = super().get_queryset()


        city = self.request.query_params.get('city',None)
        if city is not None:
            city = city
            queryset =  queryset.filter(city=city)

        country = self.request.query_params.get('country',None)
        if country is not None:
            country = country
            queryset =  queryset.filter(country=country)
        
        
        user = self.request.user
        if user.is_authenticated and (user.is_admin() or user.is_agent):
            return queryset

       

        return queryset.filter(user=user.id)
    
    


    



#Loan request view set
class LoanModelViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [CanEditLoanRequest, IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['start_date']
    renderer_classes = [TemplateHTMLRenderer]

    def get_serializer_class(self):
        if self.request.user.is_customer:
            return CustomerLoanSerializer
        return LoanSerializer

    @action(methods=["GET", "POST"], detail=False, permission_classes=[CanEditLoanRequest, IsAuthenticated])
    def blank_form(self, request, *args, **kwargs):
        """
        Renders form to apply for loan-request
        """
        serializer = LoanSerializer()

        if request.user.is_customer:
            serializer = CustomerLoanSerializer()

        return Response(
            {'serializer': serializer, "new": True},
            template_name="applyloan.html"
        )

    @action(methods=["GET", "POST"], detail=True, permission_classes=[CanEditLoanRequest, IsAuthenticated])
    def edit(self, request, pk):
        """
        Renders form to edit loan-request
        """
        if request.method == "POST":
            loan = get_object_or_404(Loan, pk=pk)
            if request.user.is_agent and loan.status != 'approved':
                return self.update(request, pk)
            else:
                raise PermissionDenied()
        return self.retrieve(request, pk)

    def list(self, request):
        queryset = self.get_queryset()
        if request.GET.get('customer'):
            customer = CustomerProfile.objects.filter(
                id=int(request.GET.get('customer'))
            ).first()
            if not customer:
                return Response(template_name='errors/404.html')
            queryset = queryset.filter(customer=customer.id)

        return Response(
            {"loan_requests": queryset},
            template_name='loan-requests.html'
        )

    def retrieve(self, request, pk=None):
        super(self.__class__, self).retrieve(request, pk)
        loan = get_object_or_404(Loan, pk=pk)
        return Response(
            {'serializer': self.get_serializer_class()(loan), "loan": pk},
            template_name='applyloan.html',
        )

    def perform_create(self, serializer):
        if self.request.user.is_customer:
            serializer.save(customer=self.request.user.customer, interest_rate=settings.INTEREST_RATE[self.request.data['loan_type']])
        else:
            serializer.save()

    def create(self, request):

        # Customer can not create loan for another customer
        if request.user.is_customer and request.data.get("customer") \
                and request.user.customer.id != int(request.data.get("customer")):
            raise PermissionDenied()
        super(self.__class__, self).create(request)
        messages.success(request, "Loan Request has been added successfully!")
        return redirect(reverse('loan-list'))

    def update(self, request, pk=None):
        loan = get_object_or_404(Loan, pk=pk)
        super(self.__class__, self).update(request, pk)
        messages.success(request, "Loan Request has been updated successfully!")
        return redirect(reverse('loan-detail', kwargs={'pk': pk}))

    def destroy(self, request, pk=None):
        super(self.__class__, self).destroy(request, pk)
        return redirect(reverse('loan-list'))

    def get_queryset(self):
        """
        Show all loan-requests to agent and show customer only their
        own loan-requests
        """
        queryset = super().get_queryset()

        start_date = self.request.query_params.get('start_date',None)
        if start_date is not None:
            start_date = start_date
            queryset =  queryset.filter(start_date__date=start_date)

        end_date = self.request.query_params.get('end_date',None)
        if end_date is not None:
            end_date = end_date
            queryset =  queryset.filter(end_date__date=end_date)


        tenure = self.request.query_params.get('tenure',None)
        if tenure is not None:
            tenure = tenure
            queryset =  queryset.filter(tenure=tenure)


        status = self.request.query_params.get('status',None)
        if status is not None:
            status = status
            queryset =  queryset.filter(status=status)


        user = self.request.user
        if user.is_authenticated and (user.is_admin() or user.is_agent):
            return queryset

        return queryset.filter(customer__user=user.id)