from django.db.models import Case, CharField, JSONField, Count, F, Value, When, Sum, Avg, FloatField
from django.db.models.functions import ExtractMonth, ExtractYear
from django.http import JsonResponse, Http404
from django.shortcuts import render
from .models import Invoice
from django.db.models.functions import Round

month_map = (
    Case(
        When(month_id=1, then=Value("January")),
        When(month_id=2, then=Value("February")),
        When(month_id=3, then=Value("March")),
        When(month_id=4, then=Value("April")),
        When(month_id=5, then=Value("May")),
        When(month_id=6, then=Value("June")),
        When(month_id=7, then=Value("July")),
        When(month_id=8, then=Value("August")),
        When(month_id=9, then=Value("September")),
        When(month_id=10, then=Value("October")),
        When(month_id=11, then=Value("November")),
        When(month_id=12, then=Value("December")),
            output_field=CharField())
)

context = {
    'invoices_info': None,
    'view_type': None,
    'selected_customer': None,
    'selected_year': None,
    'selected_month': None,
}

def get_invoices_year(invoices_info, customer_id_query):
    context['view_type'] = 'years'
    context['selected_customer'] = invoices_info.filter(customer_id=customer_id_query).values_list('customer_name', flat=True).first()

    invoices_info = invoices_info.filter(customer_id=customer_id_query).annotate(
        year=ExtractYear('invoice_date'),
        total_invoices=Count('id')
    ).order_by('-year')

    if not invoices_info.exists():
        raise Http404("No invoices found for the given customer_id.")
    return invoices_info

def get_invoices_month(invoices_info, year_query):
    context['view_type'] = 'months'
    context['selected_year'] = invoices_info.values_list('year', flat=True).filter(year=year_query).first()

    invoices_info = invoices_info.filter(year=year_query).annotate(
        month_id=ExtractMonth('invoice_date'),
        month_name=month_map,
        total_invoices=Count('id')
    ).order_by('-month_id')

    if not invoices_info.exists():
        raise Http404("No invoices found for the given year.")
    return invoices_info

def get_invoices_info(invoices_info, month_query):
    context['view_type'] = 'invoice_info'
    context['selected_month'] = invoices_info.values_list('month_name', flat=True).filter(month_id=month_query).first()
    
    invoices_info = invoices_info.filter(month_id=month_query)

    if not invoices_info.exists():
        raise Http404("No invoices found for the given month.")

    try:
        # Annotate invoices_info with additional fields
        source_revenue_info = (
            invoices_info
                .values('revenue_source_name', 'currency_code')
                .annotate(
                    total_adjusted_gross_value=Round(Sum('adjusted_gross_value'), 2, output_field=FloatField()),
                    available_advance=Round(
                        Sum(F('adjusted_gross_value') * (1 - F('haircut_percent') / 100))
                        , 2, output_field=FloatField()
                    ),
                    monthly_fee_amount=Round(
                        Sum(F('adjusted_gross_value') * (1 - F('haircut_percent') / 100) * (F('daily_advance_fee') / 100))
                        , 2, output_field=FloatField()
                    ),
                    total_invoices=Count('id'),
                )
                .order_by('-total_adjusted_gross_value')
        )

        # Merge source_revenue info with invoices_info
        invoices_info = invoices_info.annotate(
            source_revenue_info=Value(list(source_revenue_info), output_field=JSONField())
        )
    except Exception as e:
        raise Http404(f"Error processing invoices: {str(e)}")
    
    return invoices_info

def get_invoices(request):
    # Validate request
    if not request:
        return JsonResponse({"error": "Invalid request"}, status=400)
    if request.method != 'GET':
        return JsonResponse({"error": "GET request required"}, status=400)
    
    # Get query parameters from request
    customer_id_query = request.GET.get('customer_id', None)
    year_query = request.GET.get('year', None)
    month_query = request.GET.get('month', None)
    
    # Initialize context
    context['view_type'] = 'customers'
    invoices_info = Invoice.objects.values(
        'customer_name', 
        'customer_id',
    ).annotate(
        total_invoices=Count('id')
    ).order_by('customer_name').distinct()

    if not invoices_info.exists():
        raise Http404("No invoices found.")

    # Filter invoices based on query parameters
    if customer_id_query:
        invoices_info = get_invoices_year(invoices_info, customer_id_query)
    if customer_id_query and year_query:
        invoices_info = get_invoices_month(invoices_info, year_query)
    if customer_id_query and year_query and month_query:
        invoices_info = get_invoices_info(invoices_info, month_query)

    context['invoices_info'] = invoices_info

    # Check if the request is for JSON response
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(list(context["invoices_info"]), safe=False)
    return render(request, "invoices/index.html", context)

