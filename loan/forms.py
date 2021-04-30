from django.contrib.auth.forms import UserCreationForm
from django_countries.fields import CountryField
from django import forms
from .models import User,CustomerProfile, Loan
from django.forms import ModelForm
from django.contrib.auth.models import Group
class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=(('agent', "Agent"), ("customer", "Customer")), widget=forms.Select(),
        label="Register as", required=True
    )
    phone = forms.IntegerField(required=True)
    street_address = forms.CharField(required=True)
    zip_code = forms.CharField(required=True)
    city = forms.CharField(required=True)
    country= CountryField().formfield()
    first_name= forms.CharField(required=True)
    last_name= forms.CharField(required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name",
            "username", "email", "password1",
            "password2", "role", "phone", "street_address",
            "zip_code", "city", "country"
        )

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_customer = self.cleaned_data['role'] == "customer"
        user.is_agent = self.cleaned_data['role'] == "agent"

        # Prevent user from login, until approved by admin
        user.is_active = False

        if user.is_agent:
            user.is_staff = True

        if commit:
            user.save()

            if user.is_agent:
                agent_group = Group.objects.get(name='Agent')
                agent_group.user_set.add(user)
            # Create customer profile for user
            if user.is_customer:
                CustomerProfile.objects.create(
                    user=user,
                    phone=self.cleaned_data['phone'],
                    street_address=self.cleaned_data['street_address'],
                    zip_code=self.cleaned_data['zip_code'],
                    city=self.cleaned_data['city'],
                    country=self.cleaned_data['country'],
                )

        return user


class LoanInputForm(ModelForm):
    #customer = forms.ModelChoiceField(queryset=None)
    #loan_type = forms.ChoiceField(choices=(('house', 'Home Loan'),('car', 'Car loan'),('personal', 'personal')), widget=forms.Select(),label="Loan type", required=True)
    #amount = forms.DecimalField(required=True)
    #tenure = forms.IntegerField(required=True)
    #interest_rate = forms.DecimalField(required=True)
    


    class Meta:
        model = Loan
        fields = ['loan_type', 'amount', 'tenure', 'interest_rate']


    def save(self, commit=True, user=None):

        loan = super(LoanInputForm,self).save(commit=False)
        if user and user.is_customer:
            customer = CustomerProfile.objects.filter(user=user.id).first()
        elif user and user.is_agent:
            pass
            #todo crete new user and customer profile for that user
        print("heloooooooooooooooooooooo",customer)
        loan.customer = customer
        if commit:
            loan.save()