from django.contrib import admin

from .models import Loan, User, CustomerProfile


class LoanAdmin(admin.ModelAdmin):
    date_hierarchy = 'modified'
    ordering = ('-modified',)
    list_display = (
        'customer', 'amount', 'loan_type', 'tenure', 'interest_rate',
        'status', "emi"
    )
    readonly_fields = ("emi", "start_date", "end_date", "principal_amount")

    def get_readonly_fields(self, request, obj=None):
        if obj and not request.user.is_admin:
            return self.readonly_fields + ('status')
        elif obj and obj.status == "approved":
            return [field.name for field in self.model._meta.get_fields()]
        return self.readonly_fields

admin.site.register(Loan, LoanAdmin)
admin.site.register(User)
admin.site.register(CustomerProfile)


    

# Register your models here.
