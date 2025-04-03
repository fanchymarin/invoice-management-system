from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import ExtractYear, ExtractMonth
from .models import Invoice
from django.http import JsonResponse

context = {
    'invoices_info': None,
    'view_type': None,
    'selected_customer': None,
}

def get_invoices_year(invoices_info, customer_id_query):
    context['view_type'] = 'years'
    invoices_info = invoices_info.filter(customer_id=customer_id_query).annotate(
        year=ExtractYear('invoice_date')
    ).values('year').annotate(total_invoices=Count('id')).order_by('-year')
    
    customer_name = Invoice.objects.filter(customer_id=customer_id_query).values_list('customer_name', flat=True).first()
    
    context['selected_customer'] = customer_name
    return invoices_info

def get_invoices_info(request):
    customer_id_query = request.GET.get('customer_id', None)
    year_query = request.GET.get('year', None)
    month_query = request.GET.get('month', None)
    
    invoices_info = Invoice.objects.values(
        'customer_name',
        'customer_id'
    )
    
    if customer_id_query:
        invoices_info = get_invoices_year(invoices_info, customer_id_query)
    else:
        context['view_type'] = 'customers'
        invoices_info = invoices_info.order_by('customer_name').distinct()
    
    context['invoices_info'] = invoices_info
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(list(context['invoices_info']), safe=False)
    
    return render(request, "invoices/index.html", context)

