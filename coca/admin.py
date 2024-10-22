from django.contrib import admin
from .models import Invoice, InvoiceItem

# @admin.register(Invoice)
# class InvoiceAdmin(admin.ModelAdmin):
#     list_display = ('id', 'date')  # Update fields to match the Invoice model

# @admin.register(InvoiceItem)
# class InvoiceItemAdmin(admin.ModelAdmin):
#     list_display = ('invoice', 'description', 'price', 'quantity', 'total')

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0  # Number of empty forms to display

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'date')
    inlines = [InvoiceItemInline]  # Include inline for InvoiceItem
