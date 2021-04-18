
from django.contrib import admin
from django.urls import path,include
from loan import views
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.urlpatterns import format_suffix_patterns

#creating router object
router = DefaultRouter()
router2 = DefaultRouter()

#Register ClientViewSet with Router
router.register('clientapi', views.ClientModelViewSet, basename='client')
router2.register('loanapi', views.LoanModelViewSet, basename='loan')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('loan.urls')),
    path('accounts/',include('accounts.urls')),
    path('', include(router.urls)),
    path('', include(router2.urls)),
    #path('gettoken/', obtain_auth_token)
]
