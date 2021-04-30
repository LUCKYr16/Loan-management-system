from .models import CustomerProfile, Loan
from rest_framework import serializers


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = "__all__"



class CustomerLoanSerializer(serializers.ModelSerializer):
    class Meta:
         model = Loan
         fields = ("loan_type", "amount", "tenure", "interest_rate", "customer")
         read_only_fields =  ('customer','interest_rate')

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ("loan_type", "amount", "tenure", "interest_rate", "customer") 