from django.http import JsonResponse
from django.shortcuts import redirect
from .models import Invoice
import base64
from django.contrib.auth import authenticate, login
from django.http import HttpResponseForbidden

class InvoiceAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/invoices'):
            return self.get_response(request)

        is_json_request = "application/json" in request.headers.get("Accept", "")

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if is_json_request and auth_header.startswith("Basic "):
            try:
                encoded_credentials = auth_header.split(" ")[1]
                decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
                uname, passwd = decoded_credentials.split(':', 1)
                user = authenticate(username=uname, password=passwd)
                if user and user.is_active:
                    login(request, user)
                    request.user = user
            except (IndexError, ValueError, base64.binascii.Error):
                return JsonResponse({"error": "Invalid authentication header"}, status=400)

        if not request.user.is_authenticated:
            if is_json_request:
                return JsonResponse({"error": "Authentication required"}, status=401)
            return redirect('login')

        if request.user.is_superuser:
            return self.get_response(request)

        customer_username = request.user.username
        customer_id = (Invoice.objects
                       .filter(customer_name=customer_username)
                       .values_list('customer_id', flat=True)
                       .first()
                       )
        
        if 'customer_id' in request.GET and customer_id:
            request_customer_id = request.GET.get('customer_id')
            if str(customer_id) != request_customer_id:
                if is_json_request:
                    return JsonResponse({"error": "Access denied. Invalid customer_id"}, status=403)
                return HttpResponseForbidden("Access denied. Invalid customer_id")

        if customer_id and 'customer_id' not in request.GET:
            if is_json_request:
                return JsonResponse({"error": "Missing customer_id", "customer_id": customer_id}, status=400)
            return redirect(f'/invoices/?customer_id={customer_id}')

        return self.get_response(request)