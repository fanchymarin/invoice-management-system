from .models import Invoice
from django.shortcuts import redirect

class InvoiceAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/invoices'):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect('login')
        
        if request.user.is_superuser:
            return self.get_response(request)
        
        customer_username = request.user.username
        customer_id = (Invoice.objects
                       .filter(customer_name=customer_username)
                       .values_list('customer_id', flat=True)
                       .first()
                       )
        if customer_id and 'customer_id' not in request.GET:
            return redirect(f'/invoices/?customer_id={customer_id}')
        else:
            return self.get_response(request)