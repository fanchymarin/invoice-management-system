from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import ExtractYear, ExtractMonth
from .models import Invoice
from django.http import JsonResponse

def get_invoices_info(request):

    customer_id_query = request.GET.get('customer_id', None)
    year_query = request.GET.get('year', None)
    month_query = request.GET.get('month', None)

    invoices_info = Invoice.objects.values(
        'customer_name',
        'customer_id'
        )
    
    if customer_id_query:
        invoices_info = invoices_info.filter(customer_id=customer_id_query).annotate(
            year=ExtractYear('invoice_date')
        ).order_by('-invoice_date')
        render_html = "invoices/years.html"

    else:
        invoices_info = invoices_info.order_by('customer_name').distinct()
        render_html = "invoices/index.html"


    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(list(invoices_info), safe=False)
    return render(request, render_html, {'invoices_info': invoices_info})
