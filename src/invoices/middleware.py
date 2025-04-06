from django.http import JsonResponse
from django.shortcuts import redirect
from .models import Invoice
import base64
from django.contrib.auth import authenticate, login
from django.core.exceptions import PermissionDenied

class InvoiceAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/invoices'):
            return self.get_response(request)

        is_json_request = "application/json" in request.headers.get("Accept", "")

        # Manually handle Basic Authentication for API requests
        if is_json_request:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith("Basic "):
                try:
                    encoded_credentials = auth_header.split(" ")[1]
                    decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
                    uname, passwd = decoded_credentials.split(':', 1)
                    user = authenticate(username=uname, password=passwd)
                    if user and user.is_active:
                        login(request, user)
                        request.user = user
                    else:
                        if is_json_request:
                            return JsonResponse({"error": "Invalid credentials"}, status=401)
                        return redirect('login')
                except (IndexError, ValueError, base64.binascii.Error):
                    return JsonResponse({"error": "Invalid authentication header"}, status=400)
            else:
                if is_json_request:
                    return JsonResponse({"error": "Basic authentication required"}, status=401)
                return redirect('login')

        if request.user.is_superuser:
            return self.get_response(request)

        # Match customer username with Invoices.customer_id
        customer_username = request.user.username
        customer_id = (Invoice.objects
                       .filter(customer_name=customer_username)
                       .values_list('customer_id', flat=True)
                       .first()
                       )
        
        if not customer_id:
            if is_json_request:
                return JsonResponse({"error": "Customer not found"}, status=404)
            return redirect('login')
        
        if not request.user.is_authenticated:
            if is_json_request:
                return JsonResponse({"error": "Authentication required"}, status=401)
            return redirect('login')
        
        # Check if customer is requesting their own invoices
        if 'customer_id' in request.GET:
            if str(customer_id) != request.GET.get('customer_id'):
                if is_json_request:
                    return JsonResponse({"error": "Access denied"}, status=403)
                raise PermissionDenied()
            
        # Check if customer is requesting their all invoices
        if request.path.endswith('/invoices/') and 'customer_id' not in request.GET:
            if is_json_request:
                return JsonResponse({"error": "Access denied"}, status=403)
            return redirect(f'/invoices/?customer_id={customer_id}')
        return self.get_response(request)