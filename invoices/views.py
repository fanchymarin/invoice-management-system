from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import ExtractYear, ExtractMonth
from .models import Invoice
from django.http import JsonResponse

def invoice_list(request):

    invoices = Invoice.objects.values(
        'customer_name', 
        'revenue_source_name',
        'currency_code',
        'adjusted_gross_value',
        'haircut_percent',
        'daily_advance_fee',
        'advance_duration',
        'invoice_date'
    ).order_by('customer_name', '-invoice_date', 'revenue_source_name')

    customer_name = request.GET.get('customer_name', None)
    if customer_name:
        invoices = invoices.filter(customer_name__icontains=customer_name)
    else:
        invoices = invoices.all()

    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(list(invoices), safe=False)
    return render(request, 'invoice_list.html', {'invoices': invoices})
