from django.contrib import admin
from django.urls import path, include, re_path
from loan import views
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.urlpatterns import format_suffix_patterns

#creating router object
router = routers.DefaultRouter()
router.register(r'customers', views.CustomerModelViewSet)
router.register(r'loan-requests', views.LoanModelViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
   
    path('', include('loan.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include(router.urls)),
    path(
        'api-auth/',
        include('rest_framework.urls', namespace='rest_framework')
    ),
    path("register", views.register_request, name="register"),
    # path("applyloan/", views.applyloanview,name='applyloan'),
    # path('customer-profiles/',views.viewprofiles, name='profile'),
    # path('customer-profiles/loan-requests', views.loan_requests, name='loan-requests'),
    # path('my-profile/',views.my_profile, name='my-profile'),
    #path('gettoken/', obtain_auth_token)
]