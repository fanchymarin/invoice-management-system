import datetime
from django.test import TestCase
from .models import Invoice
import base64
from django.contrib.auth.models import User

class InvoiceTestCase(TestCase):
	def setUp(self):
		# Create users
		self.admin_user = User.objects.create_superuser(username="admin", password="admin")
		self.customer_user = User.objects.create_user(username="Test Customer", password="1234")
		Invoice.objects.create(
			adjusted_gross_value=100.00,
			haircut_percent=5.00,
			daily_advance_fee=0.50,
			advance_duration=30,
			customer_name='Test Customer',
			customer_id=1,
			revenue_source_id=1,
			revenue_source_name='Test Source',
			currency_code='USD',
			invoice_date='2023-01-01'
		)
		Invoice.objects.create(
			adjusted_gross_value=50.00,
			haircut_percent=10.00,
			daily_advance_fee=0.10,
			advance_duration=30,
			customer_name='Test Customer',
			customer_id=1,
			revenue_source_id=1,
			revenue_source_name='Test Source',
			currency_code='USD',
			invoice_date='2023-01-02'
		)
		Invoice.objects.create(
			adjusted_gross_value=200.00,
			haircut_percent=10.00,
			daily_advance_fee=15.00,
			advance_duration=60,
			customer_name='Another Customer',
			customer_id=2,
			revenue_source_id=2,
			revenue_source_name='Another Source',
			currency_code='EUR',
			invoice_date='2023-02-01'
		)

	def test_invoices_creation(self):
		invoice = Invoice.objects.get(customer_name='Test Customer', invoice_date='2023-01-01')
		self.assertEqual(invoice.adjusted_gross_value, 100.00)
		self.assertEqual(invoice.haircut_percent, 5.00)
		self.assertEqual(invoice.daily_advance_fee, 0.50)
		self.assertEqual(invoice.advance_duration, 30)
		self.assertEqual(invoice.customer_id, 1)
		self.assertEqual(invoice.revenue_source_id, 1)
		self.assertEqual(invoice.revenue_source_name, 'Test Source')
		self.assertEqual(invoice.currency_code, 'USD')
		self.assertEqual(invoice.invoice_date, datetime.date(2023, 1, 1))

	def test_invoices_count(self):
		invoice_count = Invoice.objects.count()
		self.assertEqual(invoice_count, 3)

	def test_no_param_query(self):
		credentials = base64.b64encode(b'admin:admin').decode('utf-8')
		response = self.client.get(
            '/invoices/', 
            HTTP_ACCEPT='application/json', 
            HTTP_AUTHORIZATION=f'Basic {credentials}'
        )
		
		self.assertJSONEqual(
			str(response.content, encoding='utf8'),
			[
				{
					"customer_name": "Another Customer",
					"customer_id": 2,
					"total_invoices": 1
				},
				{
					"customer_name": "Test Customer",
					"customer_id": 1,
					"total_invoices": 2
				}
			]
		)
		self.assertEqual(response.status_code, 200)

	def test_customer_param_query(self):
		credentials = base64.b64encode(b'admin:admin').decode('utf-8')
		response = self.client.get(
            '/invoices/?customer_id=2', 
            HTTP_ACCEPT='application/json', 
            HTTP_AUTHORIZATION=f'Basic {credentials}'
        )

		self.assertJSONEqual(
			str(response.content, encoding='utf8'),
			[
				{
					"customer_name": "Another Customer",
					"customer_id": 2,
					"year": 2023,
					"total_invoices": 1,
				}
			]
		)
		self.assertEqual(response.status_code, 200)
	
	def test_customer_param_query_not_found(self):
		credentials = base64.b64encode(b'admin:admin').decode('utf-8')
		response = self.client.get(
            '/invoices/?customer_id=20', 
            HTTP_ACCEPT='application/json', 
            HTTP_AUTHORIZATION=f'Basic {credentials}'
        )
		
		self.assertEqual(response.status_code, 404)

	def test_year_param_query(self):
		credentials = base64.b64encode(b'admin:admin').decode('utf-8')
		response = self.client.get(
            '/invoices/?customer_id=1&year=2023', 
            HTTP_ACCEPT='application/json', 
            HTTP_AUTHORIZATION=f'Basic {credentials}'
        )

		self.assertJSONEqual(
		str(response.content, encoding='utf8'),
			[
				{
					"customer_name": "Test Customer",
					"customer_id": 1,
					"year": 2023,
					"total_invoices": 2,
					"month_id": 1,
					"month_name": "January"
				}
			]
		)
		self.assertEqual(response.status_code, 200)

	def test_year_param_query_not_found(self):
		credentials = base64.b64encode(b'admin:admin').decode('utf-8')
		response = self.client.get(
            '/invoices/?customer_id=1&year=2029', 
            HTTP_ACCEPT='application/json', 
            HTTP_AUTHORIZATION=f'Basic {credentials}'
        )

		self.assertEqual(response.status_code, 404)

	def test_month_param_query(self):
		credentials = base64.b64encode(b'admin:admin').decode('utf-8')
		response = self.client.get(
            '/invoices/?customer_id=1&year=2023&month=1', 
            HTTP_ACCEPT='application/json', 
            HTTP_AUTHORIZATION=f'Basic {credentials}'
        )

		self.assertJSONEqual(
		str(response.content, encoding='utf8'),
			[
				{
					"customer_name": "Test Customer",
					"customer_id": 1,
					"total_invoices": 2,
					"year": 2023,
					"month_id": 1,
					"month_name": "January",
					"source_revenue_info": [
						{
							"currency_code": "USD",
							"total_invoices": 2,
							"available_advance": 140,
							'monthly_fee_amount': 0.52,
							"revenue_source_name": "Test Source",
							"total_adjusted_gross_value": 150.0,

							# Calculations:
							# Total Adjusted Gross Value = 100.0 + 50.0 = 150.0
							# Available Advance = (100 * (1 - 5 / 100)) + (50 * (1 - 10 / 100)) = 95 + 45 = 140
							# Monthly Fee Amount = (95 * (0.50 / 100)) + (45 * (0.10 / 100)) = 0.475 + 0.045 = 0.52
						}
					]
				}
			]
		)
		self.assertEqual(response.status_code, 200)

	def test_month_param_query_not_found(self):
		credentials = base64.b64encode(b'admin:admin').decode('utf-8')
		response = self.client.get(
            '/invoices/?customer_id=1&year=2023&month=13', 
            HTTP_ACCEPT='application/json', 
            HTTP_AUTHORIZATION=f'Basic {credentials}'
        )

		self.assertEqual(response.status_code, 404)

	def test_user_valid_access(self):
		credentials = base64.b64encode(b'Test Customer:1234').decode('utf-8')
		response = self.client.get(
			'/invoices/?customer_id=1', 
			HTTP_ACCEPT='application/json', 
			HTTP_AUTHORIZATION=f'Basic {credentials}'
		)

		self.assertJSONEqual(
			str(response.content, encoding='utf8'),
			[
				{
					"customer_name": "Test Customer",
					"customer_id": 1,
					"year": 2023,
					"total_invoices": 2
				}
			]
		)
		self.assertEqual(response.status_code, 200)

	def test_user_invalid_access(self):
		credentials = base64.b64encode(b'Test Customer:1234').decode('utf-8')
		response = self.client.get(
			'/invoices/', 
			HTTP_ACCEPT='application/json', 
			HTTP_AUTHORIZATION=f'Basic {credentials}'
		)

		self.assertJSONEqual(
			str(response.content, encoding='utf8'),
			{
				"error": "Access denied"
			}
		)
		self.assertEqual(response.status_code, 403)

	def test_no_user_found(self):
		credentials = base64.b64encode(b'admin:wrongpassword').decode('utf-8')
		response = self.client.get(
			'/invoices/', 
			HTTP_ACCEPT='application/json', 
			HTTP_AUTHORIZATION=f'Basic {credentials}'
		)

		self.assertJSONEqual(
			str(response.content, encoding='utf8'),
			{
				"error": "Invalid credentials"
			}
		)
		self.assertEqual(response.status_code, 401)

	def test_no_authorization(self):
		credentials = base64.b64encode(b'Test Customer:1234').decode('utf-8')
		response = self.client.get(
			'/invoices/', 
			HTTP_ACCEPT='application/json', 
			HTTP_AUTHORIZATION=f'Basic {credentials}'
		)

		self.assertJSONEqual(
			str(response.content, encoding='utf8'),
			{
				"error": "Access denied"
			}
		)
		self.assertEqual(response.status_code, 403)

	def test_no_authentication(self):
		response = self.client.get(
			'/invoices/', 
			HTTP_ACCEPT='application/json'
		)

		self.assertJSONEqual(
			str(response.content, encoding='utf8'),
			{
				"error": "Basic authentication required"
			}
		)
		self.assertEqual(response.status_code, 401)
