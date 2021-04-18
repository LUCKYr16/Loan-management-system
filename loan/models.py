from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime
from django.conf import settings  
from django.contrib.auth.models import AbstractUser
#from model_utils import FieldTracker 

TYPE =   [('house', 'Home Loan'),('car', 'Car loan'),('personal', 'personal')]

STATUS = [('new','New'),('rejected','Rejeted'),('approved', 'Approved')]

roles = [('customer','Customer'),('agent','Agent'),('superuser','Superuser')]


# Create your models here.
class User(AbstractUser):
    role = models.CharField(max_length=20,choices=roles,default='superuser')


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modeified = models.DateTimeField(auto_now=True)


class Client(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone=models.CharField(max_length=10)
    address = models.JSONField(null=True)
    
    

class Loan(BaseModel):
    customer = models.ForeignKey(Client, on_delete=models.CASCADE)
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

    def save(self, *args, **kwargs):
        if self.status == "approved" and not self.start_date and not self.end_date:
            self.start_date = timezone.now()
            self.end_date = timezone.now() + relativedelta(months=self.tenure)
            #todo principal_amount
            if not self.principal_amount:
                self.principal_amount = self.amount
            self.emi = self.calculate_emi()
        return super(Loan, self).save(*args, **kwargs)

    def calculate_emi(self):
        i = ((self.amount)*(self.interest_rate)*(self.tenure))/(12*100)
        emi = (self.amount + i)/12
        return emi
        
        


    
    



