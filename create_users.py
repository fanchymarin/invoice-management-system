from django.contrib.auth.models import User
from invoices.models import Invoice

customers_info = Invoice.objects.values(
    'customer_name',
    'customer_id',
).order_by('customer_name').distinct()

for customer in customers_info:
    User.objects.create_user(
        username=customer['customer_name'],
        password='1234',
        email=customer['customer_name'] + '@example.com',
    )
    print(f"User {customer['customer_name']} created.")