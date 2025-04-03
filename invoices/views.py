from django.shortcuts import render
from django.db.models import Sum, Count, CharField
from django.db.models.functions import ExtractYear, ExtractMonth
from .models import Invoice
from django.http import JsonResponse
import calendar

context = {
    'invoices_info': None,
    'view_type': None,
    'selected_customer': None,
    'selected_year': None,
    'selected_month': None,
}

def get_invoices_year(invoices_info, customer_id_query):
    context['view_type'] = 'years'
    invoices_info = invoices_info.filter(customer_id=customer_id_query).annotate(
        year=ExtractYear('invoice_date'),
        total_invoices=Count('id')
    ).order_by('-year')
    
    context['selected_customer'] = invoices_info.values_list('customer_name', flat=True).first()
    return invoices_info

def get_invoices_month(invoices_info, year_query):
    context['view_type'] = 'months'
    invoices_info = invoices_info.filter(year=year_query).annotate(
        month=ExtractMonth('invoice_date'),
        total_invoices=Count('id')
    ).order_by('-month')

    context['selected_year'] = invoices_info.values_list('year', flat=True).first()
    return invoices_info

def get_invoices_info(request):
    # Get query parameters
    customer_id_query = request.GET.get('customer_id', None)
    year_query = request.GET.get('year', None)
    month_query = request.GET.get('month', None)
    
    # Initialize context
    invoices_info = Invoice.objects.values(
        'customer_name', 
        'customer_id',
    ).order_by('customer_name').distinct()
    context['view_type'] = 'customers'

    # Filter invoices based on query parameters
    if customer_id_query:
        invoices_info = get_invoices_year(invoices_info, customer_id_query)
    if year_query:
        invoices_info = get_invoices_month(invoices_info, year_query)

    context['invoices_info'] = invoices_info
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(list(context["invoices_info"]), safe=False)
    
    return render(request, "invoices/index.html", context)

