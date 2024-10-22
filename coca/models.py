# coca/models.py

from django.db import models
from django.utils import timezone

class Invoice(models.Model):
    date = models.DateField(default=timezone.now)  # Correct default
    installment1_amount = models.FloatField(default=0.0)
    installment1_date = models.DateField(default=timezone.now)  # Correct default
    installment2_amount = models.FloatField(default=0.0)
    installment2_date = models.DateField(default=timezone.now)  # Correct default

    def __str__(self):
        return f"Invoice {self.id} - {self.date}"

class InvoiceItem(models.Model):
    student_name = models.CharField(max_length=255)
    parent_name = models.CharField(max_length=255)
    student_contact = models.CharField(max_length=20)
    parent_contact = models.CharField(max_length=20)
    course = models.CharField(max_length=255)
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.TextField(default='No Description')
    price = models.FloatField(default=0.0)
    quantity = models.IntegerField(default=1)
    
    # New Fields
    degree = models.CharField(max_length=255, default='N/A')
    passed_out_year = models.IntegerField(default=0)
    address = models.TextField(default='N/A')
    validity_date = models.DateField(default=timezone.now)  # Correct default
    duration = models.IntegerField(default=0)  # Duration in months

    def total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.course} - {self.student_name}"
