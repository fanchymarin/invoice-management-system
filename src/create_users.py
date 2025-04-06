from django.contrib.auth.models import User
from invoices.models import Invoice

customers_info = Invoice.objects.values(
    'customer_name',
    'customer_id',
).order_by('customer_name').distinct()

for customer in customers_info:
    try:
        User.objects.create_user(
            username=customer['customer_name'],
            password='1234',
            email=customer['customer_name'] + '@example.com',
        )
        print(f"User {customer['customer_name']} created.")
    except Exception as e:
        if 'duplicate key value violates unique constraint' in str(e):
            print(f"User {customer['customer_name']} already exists.")
        else:
            print(f"Error creating user {customer['customer_name']}: {e}")