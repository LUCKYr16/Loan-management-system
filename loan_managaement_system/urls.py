from django.contrib import admin
from django.urls import path, include
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
    path('actions/api/', include(router.urls)),
    path(
        'api-auth/',
        include('rest_framework.urls', namespace='rest_framework')
    ),
    path("register", views.register_request, name="register"),
    path("applyloan/", views.applyloanview,name='applyloan'),
    path("actions/", views.actions, name='action'),
    path('actions/show/',views.userprofile, name = 'userprofile'),
    path('profile/',views.viewprofiles, name='table'),
    path('profile/loanrequests',views.loanrequests, name='loanreq'),
    #path('gettoken/', obtain_auth_token)
]