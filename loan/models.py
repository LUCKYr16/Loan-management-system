from django.db import models
from django.contrib.auth.models import AbstractUser



# Create your models here.
class Client(models.Model):
	name=models.CharField(max_length=50)
	email=models.EmailField(max_length=50)
	phone=models.CharField(max_length=10)
	city=models.CharField(max_length=50)


TYPE =   [ 
			    ('house', 'Home Loan'),
			    ('car', 'Car loan'),
			    ('personal', 'personal'),
	]

STATUS = [
		('new','New'),
		('rejected','Rejeted'),
		('approved', 'Approved')
	]	

class Loan(models.Model):
    loan_type = models.CharField(max_length=50,choices=TYPE)
    amount = models.IntegerField()
    tenure = models.IntegerField()
	



