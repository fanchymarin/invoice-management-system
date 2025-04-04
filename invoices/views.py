from django.db.models import Case, CharField, Count, DecimalField, JSONField, Value, When
from django.db.models.functions import Coalesce, ExtractMonth, ExtractYear
from django.http import JsonResponse, Http404
from django.shortcuts import render
from .models import Invoice

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
        month_name=Case(
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
            output_field=CharField(),
        ),
        total_invoices=Count('id')
    ).order_by('-month_id')

    if not invoices_info.exists():
        raise Http404("No invoices found for the given year.")
    return invoices_info

def unify_invoice_sources(data):
    result = []
    
    for invoice_info in data:
        unified_sources = {}
        
        # Initialize unified sources
        for entry in invoice_info["invoice_sources"]:
            key = entry["revenue_source_name"], entry["currency_code"]
            if key in unified_sources:
                unified_sources[key]["total_adjusted_gross_value"] += entry["adjusted_gross_value"]
                unified_sources[key]["monthly_haircut_percent"] += entry["haircut_percent"]
                unified_sources[key]["monthly_advance_fee"] += entry["daily_advance_fee"]
                unified_sources[key]["monthly_advance_duration"] += entry["advance_duration"]
                unified_sources[key]["total_invoices"] += 1
            else:
                unified_sources[key] = {
                    "revenue_source_name": entry["revenue_source_name"],
                    "currency_code": entry["currency_code"],
                    "total_adjusted_gross_value": entry["adjusted_gross_value"],
                    "total_invoices": entry["total_invoices"],
                    "monthly_haircut_percent": entry["haircut_percent"],
                    "monthly_advance_fee": entry["daily_advance_fee"],
                    "monthly_advance_duration": entry["advance_duration"],
                    "available_advance": entry["available_advance"],
                }
    
        # Calculate means for monthly params, available advance and daily fee amount
        for entry in unified_sources:
            unified_sources[entry]["monthly_haircut_percent"] = float(round(
                unified_sources[entry]['monthly_haircut_percent'] / unified_sources[entry]['total_invoices'], 2
            ))          
            unified_sources[entry]["available_advance"] = float(round(
                unified_sources[entry]['total_adjusted_gross_value'] * (1 - unified_sources[entry]['monthly_haircut_percent'] / 100), 2
            ))
            unified_sources[entry]["monthly_advance_duration"] = round(
                unified_sources[entry]['monthly_advance_duration'] / unified_sources[entry]['total_invoices']
            )
  
        # Convert unified sources to list and sort
        unified_list = list(unified_sources.values())
        unified_list.sort(key=lambda x: x["total_adjusted_gross_value"], reverse=True)
        
        # Replace the original invoice sources with the unified list
        new_invoice_info = invoice_info.copy()
        new_invoice_info["invoice_sources"] = unified_list
        result.append(new_invoice_info)
    
    return result


def get_invoices_info(invoices_info, month_query):
    context['view_type'] = 'invoice_info'
    context['selected_month'] = invoices_info.values_list('month_name', flat=True).filter(month_id=month_query).first()
    
    invoices_info = invoices_info.filter(month_id=month_query)

    if not invoices_info.exists():
        raise Http404("No invoices found for the given month.")

    total_amount_by_source_revenue = (
        invoices_info
        .values('revenue_source_name',
                'adjusted_gross_value',
                'currency_code',
                'haircut_percent',
                'advance_duration',
                'daily_advance_fee',
                )
        .annotate(
            total_invoices=Count('id'),
            available_advance=Coalesce(0, 0, output_field=DecimalField()),
        )
        .order_by('-adjusted_gross_value')
    )

    for entry in total_amount_by_source_revenue:
        entry['adjusted_gross_value'] = float(round(
            entry['adjusted_gross_value'], 2))
        entry['haircut_percent'] = float(round(
            entry['haircut_percent'], 2))
        entry['daily_advance_fee'] = float(round(
            entry['daily_advance_fee'], 2))
        entry['available_advance'] = float(round(
            entry['available_advance'], 2))

    invoices_info = invoices_info.annotate(
        invoice_sources=Value(list(total_amount_by_source_revenue), output_field=JSONField())
    )

    invoices_info = unify_invoice_sources(invoices_info)
    return invoices_info

def get_customers(request):
    # Validate request
    if not request:
        return JsonResponse({"error": "Invalid request"}, status=400)
    if request.method != 'GET':
        return JsonResponse({"error": "GET request required"}, status=400)
    
    # Get query parameters
    customer_id_query = request.GET.get('customer_id', None)
    year_query = request.GET.get('year', None)
    month_query = request.GET.get('month', None)
    
    # Initialize context
    invoices_info = Invoice.objects.values(
        'customer_name', 
        'customer_id',
    ).annotate(
        total_invoices=Count('id')
    ).order_by('customer_name').distinct()
    context['view_type'] = 'customers'

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

