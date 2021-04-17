from django.contrib import admin
from loan import views
from django.urls import path,include

urlpatterns = [
   path("", views.index,name='loan'),
   path("applyloan",views.applyloan, name='apply'),
   
]