import datetime
from django.test import TestCase
from .models import Invoice

class InvoiceTestCase(TestCase):
	def setUp(self):
		# Create some test data
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
		invoice = Invoice.objects.get(customer_name='Test Customer', id=1)
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

	def test_get_customers(self):
		response = self.client.get('/invoices/', HTTP_ACCEPT='application/json')
		
		self.assertEqual(response.status_code, 200)
		self.assertJSONEqual(
			str(response.content, encoding='utf8'),
			[
				{
					"customer_name": "Another Customer",
					"customer_id": 2
				},
				{
					"customer_name": "Test Customer",
					"customer_id": 1
				}
			]
		)

	def test_customer_param_query(self):
		response = self.client.get('/invoices/?customer_id=2', HTTP_ACCEPT='application/json')

		self.assertEqual(response.status_code, 200)
		self.assertJSONEqual(
			response.content,
			[
				{
					"customer_name": "Another Customer",
					"customer_id": 2,
          "year": 2023,
          "total_invoices": 1,
        }
      ]
		)
	
	def test_customer_param_query_not_found(self):
		response = self.client.get('/invoices/?customer_id=10', HTTP_ACCEPT='application/json')
		self.assertEqual(response.status_code, 404)

	def test_year_param_query(self):
		response = self.client.get('/invoices/?customer_id=1&year=2023', HTTP_ACCEPT='application/json')

		self.assertEqual(response.status_code, 200)
		self.assertJSONEqual(
      response.content,
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

	def test_year_param_query_not_found(self):
		response = self.client.get('/invoices/?customer_id=1&year=2025', HTTP_ACCEPT='application/json')
		self.assertEqual(response.status_code, 404)

	def test_month_param_query(self):
		response = self.client.get('/invoices/?customer_id=1&year=2023&month=1', HTTP_ACCEPT='application/json')

		self.assertEqual(response.status_code, 200)
		self.assertJSONEqual(
      response.content,
        [
          {
            "customer_name": "Test Customer",
            "customer_id": 1,
            "year": 2023,
            "total_invoices": 2,
            "month_id": 1,
            "month_name": "January",
            "invoice_sources": [
              {
                "revenue_source_name": "Test Source",
                "currency_code": "USD",
                "total_adjusted_gross_value": 150.0,
                "total_invoices": 2,
                "monthly_haircut_percent": 7.5,
                "monthly_advance_fee": 0.60,
                "monthly_advance_duration": 30,
                "available_advance": 138.75,
              }
            ]
          }
        ]
      )

	def test_month_param_query_not_found(self):
		response = self.client.get('/invoices/?customer_id=1&year=2023&month=13', HTTP_ACCEPT='application/json')
		self.assertEqual(response.status_code, 404)
