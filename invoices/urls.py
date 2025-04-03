from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_customers, name='get_customers'),
]
