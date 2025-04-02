from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_invoices_info, name='get_invoices_info'),
]
