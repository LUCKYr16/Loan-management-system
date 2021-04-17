
from django.contrib import admin
from django.urls import path,include
from loan import views
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.urlpatterns import format_suffix_patterns

#creating router object
router = DefaultRouter()


#Register ClientViewSet with Router
router.register('clientapi', views.ClientModelViewSet, basename='client')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('loan.urls')),
    path('accounts/',include('accounts.urls')),
    path('', include(router.urls)),
    #path('gettoken/', obtain_auth_token)
]
