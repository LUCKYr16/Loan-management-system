from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django_countries.fields import CountryField
from dateutil.relativedelta import relativedelta
from model_utils import FieldTracker 

TYPE =   [('home', 'Home Loan'),('car', 'Car loan'),('personal', 'personal')]
STATUS = [('new','New'),('rejected','Rejeted'),('approved', 'Approved')]

# Create your models here.

#User model
class User(AbstractUser):
    is_agent = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    def save(self, *args, **kwargs):
        if self.is_active and self.is_agent:
            self.is_staff = True
        return super(User, self).save(*args, **kwargs)

    def is_admin(self):
        return self.is_superuser | bool(self.groups.filter(name__in=["Admin"]))


#Base
class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


#Customer profiles
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


#Loan model
class Loan(BaseModel):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=50,choices=TYPE)
    amount = models.DecimalField(max_digits=20,decimal_places=10)
    tenure = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=20,decimal_places=10)
    emi = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    principal_amount = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    status = models.CharField(max_length=50, choices= STATUS,default ='new')
    amount_paid = models.DecimalField(
        max_digits=20, decimal_places=10, null=True, blank=True
    )
    no_of_emi_left = models.IntegerField(null=True, blank=True)

    tracker = FieldTracker()

    def __str__(self):
        return "Loan Request for %s" % self.customer.user.first_name

    def save(self, *args, **kwargs):
        if self.status == "approved" and not self.start_date and not self.end_date:
            self.start_date = timezone.now()
            self.end_date = timezone.now() + relativedelta(months=self.tenure)
            self.principal_amount = self.amount
            self.no_of_emi_left = self.tenure
        if self.amount_paid:
            self.no_of_emi_left = self.tenure - 1
            self.principal_amount = self.amount - self.amount_paid
        if self.status == "approved" and self.tracker.has_changed("principal_amount"):
            self.emi = self.calculate_emi()
        return super(Loan, self).save(*args, **kwargs)

    def calculate_emi(self):
        i = (self.principal_amount)*(self.interest_rate)*(self.tenure)/(12*100)
        emi = (self.principal_amount + i)/self.tenure
        return emi