from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime
from django.conf import settings
from django_countries.fields import CountryField
from dateutil.relativedelta import relativedelta
from django.forms import ModelForm
#from model_utils import FieldTracker 

TYPE =   [('house', 'Home Loan'),('car', 'Car loan'),('personal', 'personal')]

STATUS = [('new','New'),('rejected','Rejeted'),('approved', 'Approved')]

# Create your models here.
class User(AbstractUser):
    is_agent = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)

    def is_admin(self):
        return self.is_superuser | bool(self.groups.filter(name__in=["Admin"]))

class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

class CustomerProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='customer')
    phone=models.CharField(max_length=10)
    street_address = models.CharField(max_length=1024)
    zip_code = models.CharField(max_length=12)
    city = models.CharField(max_length=1024)
    country = CountryField()

    def __str__(self):
        return "%s %s - %s, %s" % (
            self.user.first_name, self.user.last_name, self.city, self.country
        )

class Loan(BaseModel):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=50,choices=TYPE)
    amount = models.DecimalField(max_digits=20, decimal_places=10)
    tenure = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=20,decimal_places=10)
    emi = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    principal_amount = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    status = models.CharField(max_length=50, choices= STATUS,default ='new')

    #tracker = FieldTracker()
    
    def __str__(self):
        return "Loan Request for %s" % self.customer.user.first_name

    def save(self, *args, **kwargs):
        if self.status == "approved" and not self.start_date and not self.end_date:
            self.start_date = timezone.now()
            self.end_date = timezone.now() + relativedelta(months=self.tenure)
            self.principal_amount = self.amount
        if self.status == "approved":
            self.emi = self.calculate_emi()
        return super(Loan, self).save(*args, **kwargs)

    def calculate_emi(self):
        amount = self.principal_amount
        i = ((self.amount)*(self.interest_rate)*(self.tenure))/(12*100)
        emi = (self.amount + i)/12
        return emi




    