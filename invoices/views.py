from django.db.models import Case, CharField, Count, DecimalField, JSONField, Sum, Value, When
from django.db.models.functions import Coalesce, ExtractMonth, ExtractYear
from django.http import JsonResponse
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
    invoices_info = invoices_info.filter(customer_id=customer_id_query).annotate(
        year=ExtractYear('invoice_date'),
        total_invoices=Count('id')
    ).order_by('-year')
    
    context['selected_customer'] = invoices_info.values_list('customer_name', flat=True).first()
    return invoices_info

def get_invoices_month(invoices_info, year_query):
    context['view_type'] = 'months'
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

    context['selected_year'] = invoices_info.values_list('year', flat=True).first()
    return invoices_info

def unify_invoice_sources(data):
    result = []
    
    for invoice_info in data:
        unified_sources = {}
        
        for source in invoice_info["invoice_sources"]:
            key = (source["revenue_source_name"], source["currency_code"])
            
            if key in unified_sources:
                unified_sources[key]["total_adjusted_gross_value"] += source["total_adjusted_gross_value"]
                unified_sources[key]["invoice_count"] += 1
            else:
                unified_sources[key] = {
                    "revenue_source_name": source["revenue_source_name"],
                    "currency_code": source["currency_code"],
                    "total_adjusted_gross_value": source["total_adjusted_gross_value"],
                    "invoice_count": 1
                }
        
        unified_list = list(unified_sources.values())
        unified_list.sort(key=lambda x: x["total_adjusted_gross_value"], reverse=True)
        
        new_invoice_info = invoice_info.copy()
        new_invoice_info["invoice_sources"] = unified_list
        
        result.append(new_invoice_info)
    
    return result


def get_invoices_info(invoices_info, month_query):
    context['view_type'] = 'invoice_info'
    invoices_info = invoices_info.filter(month_id=month_query)

    total_amount_by_source_revenue = (
        invoices_info
        .values('revenue_source_name', 'currency_code')
        .annotate(
            total_adjusted_gross_value=Coalesce(
                Sum('adjusted_gross_value'), 0, output_field=DecimalField()))
        .order_by('-adjusted_gross_value')
    )

    for entry in total_amount_by_source_revenue:
        entry['total_adjusted_gross_value'] = float(round(entry['total_adjusted_gross_value'], 2))

        invoices_info = invoices_info.annotate(
            invoice_sources=Value(list(total_amount_by_source_revenue), output_field=JSONField())
        )

    context['selected_month'] = invoices_info.values_list('month_name', flat=True).first()
    return unify_invoice_sources(invoices_info)


def get_customers(request):
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
    if customer_id_query and year_query:
        invoices_info = get_invoices_month(invoices_info, year_query)
    if customer_id_query and year_query and month_query:
        invoices_info = get_invoices_info(invoices_info, month_query)

    context['invoices_info'] = invoices_info
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(list(context["invoices_info"]), safe=False)
    
    return render(request, "invoices/index.html", context)

