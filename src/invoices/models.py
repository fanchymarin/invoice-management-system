from django.db import models

class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    adjusted_gross_value = models.DecimalField(max_digits=10, decimal_places=2)
    haircut_percent = models.DecimalField(max_digits=5, decimal_places=2)
    daily_advance_fee = models.DecimalField(max_digits=10, decimal_places=2)
    advance_duration = models.IntegerField()
    customer_name = models.CharField(max_length=20)
    customer_id = models.IntegerField()
    revenue_source_id = models.IntegerField()
    revenue_source_name = models.CharField(max_length=30)
    currency_code = models.CharField(max_length=3)
    invoice_date = models.DateField()
    def __str__(self):
        return f"Invoice {self.id}"
