from django.shortcuts import render
from .models import Invoice

def invoice_list(request):
    customer_name = request.GET.get('customer_name', None)

    if customer_name:
        invoices = Invoice.objects.filter(customer_name__icontains=customer_name)
    else:
        invoices = Invoice.objects.all()

    return render(request, 'invoice_list.html', {'invoices': invoices, 'customer_name': customer_name})
