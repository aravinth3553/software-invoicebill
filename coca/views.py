# views.py

from django.shortcuts import render, redirect
from .models import InvoiceItem, Invoice
from django.http import JsonResponse
from escpos.printer import Network
from datetime import datetime, timedelta

def home(request):
    return render(request, 'home.html')

def billform(request):
    today = datetime.today()
    return render(request, 'billfrom.html', {'today': today})

def software(request):
    return render(request, 'software.html')

def gen_pdf(request):
    if request.method == "POST":
        try:
            # Collect form data
            student_name = request.POST.get('student')
            parent_name = request.POST.get('parent')
            student_contact = request.POST.get('student_contact')
            parent_contact = request.POST.get('parent_contact')
            amount = float(request.POST.get('amount', 0))
            date_str = request.POST.get('date')
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            course = request.POST.get('course')
            description = request.POST.get('description', 'No Description')
            
            # New Fields
            degree = request.POST.get('degree')
            passed_out_year = int(request.POST.get('passed_out_year', 0))
            address = request.POST.get('address')
            validity_date_str = request.POST.get('validity_date')
            validity_date = datetime.strptime(validity_date_str, '%Y-%m-%d').date()
            duration = int(request.POST.get('duration', 0))

            # Validate new fields as needed
            current_year = datetime.now().year
            if passed_out_year < 1900 or passed_out_year > current_year:
                raise ValueError("Invalid Passed Out Year.")
            if duration < 1:
                raise ValueError("Duration must be at least 1 month.")

            # Calculate installments
            installment1_amount = round(amount / 2, 2)
            installment2_amount = round(amount - installment1_amount, 2)
            installment1_date = date
            installment2_date = date + timedelta(days=30)

            # Create invoice
            invoice = Invoice(
                date=date,
                installment1_amount=installment1_amount,
                installment1_date=installment1_date,
                installment2_amount=installment2_amount,
                installment2_date=installment2_date
            )
            invoice.save()

            # Create invoice item with new fields
            item = InvoiceItem(
                student_name=student_name,
                parent_name=parent_name,
                student_contact=student_contact,
                parent_contact=parent_contact,
                course=course,
                invoice=invoice,
                description=description,
                price=amount,
                quantity=1,
                degree=degree,
                passed_out_year=passed_out_year,
                address=address,
                validity_date=validity_date,
                duration=duration
            )
            item.save()

            # Redirect to the billing page with invoice details
            return redirect('bill_view', invoice_id=invoice.id)

        except Exception as e:
            print(f"Error in gen_pdf: {str(e)}")
            return redirect('billform')

    else:
        return redirect('billform')

def bill_view(request, invoice_id):
    try:
        # Fetch the invoice details
        invoice = Invoice.objects.get(id=invoice_id)
        items = invoice.items.all()
        total = sum(item.total() for item in items)

        # Assuming one item per invoice; adjust if multiple items are allowed
        if items.exists():
            item = items.first()
            student_name = item.student_name
            parent_name = item.parent_name
            student_contact = item.student_contact
            parent_contact = item.parent_contact
            course = item.course
            degree = item.degree
            passed_out_year = item.passed_out_year
            address = item.address
            validity_date = item.validity_date
            duration = item.duration
            description = item.description
        else:
            student_name = "N/A"
            parent_name = "N/A"
            student_contact = "N/A"
            parent_contact = "N/A"
            course = "N/A"
            degree = "N/A"
            passed_out_year = "N/A"
            address = "N/A"
            validity_date = "N/A"
            duration = "N/A"
            description = "N/A"

        # Render the bill page with the invoice data
        return render(request, 'bill.html', {
            'invoice': invoice,
            'items': items,
            'total': total,
            'student_name': student_name,
            'parent_name': parent_name,
            'student_contact': student_contact,
            'parent_contact': parent_contact,
            'course': course,
            'degree': degree,
            'passed_out_year': passed_out_year,
            'address': address,
            'validity_date': validity_date,
            'duration': duration,
            'description': description,
        })
    except Invoice.DoesNotExist:
        return render(request, 'error.html', {'message': 'Invoice not found'})

def print_invoice(request):
    if request.method == 'POST':
        data = request.POST

        try:
            # Fetch the invoice
            invoice_id = data.get("invoice_id")
            invoice = Invoice.objects.get(id=invoice_id)
            items = invoice.items.all()

            if not items.exists():
                return JsonResponse({'status': 'error', 'message': 'No items found for this invoice.'})

            # Initialize printer
            printer = Network('192.168.1.100')  # Replace with your printer's IP address

            # Start printing
            printer.text('Vetri Technology Solutions\n')
            printer.text('Invoice\n')
            printer.text(f'Invoice ID: {invoice.id}\n')
            printer.text(f'Date: {invoice.date}\n\n')

            # Print invoice items
            for item in items:
                printer.text(f'Student: {item.student_name}\n')
                printer.text(f'Student Contact: {item.student_contact}\n')
                printer.text(f'Parent: {item.parent_name}\n')
                printer.text(f'Parent Contact: {item.parent_contact}\n')
                printer.text(f'Course: {item.course}\n')
                printer.text(f'Degree: {item.degree}\n')
                printer.text(f'Passed Out Year: {item.passed_out_year}\n')
                printer.text(f'Address: {item.address}\n')
                printer.text(f'Validity Date: {item.validity_date}\n')
                printer.text(f'Duration: {item.duration} months\n')
                printer.text(f'Description: {item.description}\n')
                printer.text(f'Quantity: {item.quantity} x ₹{item.price}\n')
                printer.text('-------------------------\n')

            # Calculate total and print
            total = sum(item.price * item.quantity for item in items)
            printer.text(f'Grand Total: ₹{total}\n')
            printer.cut()

            return JsonResponse({'status': 'success', 'message': 'Print job sent to the printer.'})

        except Invoice.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invoice not found.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error printing: {str(e)}'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})





# # coca/views.py


# from django.shortcuts import render, redirect
# from .models import InvoiceItem, Invoice
# from django.http import JsonResponse
# from escpos.printer import Network
# from datetime import datetime, timedelta

# def index(request):
#     return render(request, 'index.html')

# def billform(request):
#     return render(request, 'billfrom.html')

# def gen_pdf(request):
#     if request.method == "POST":
#         try:
#             # Collect form data
#             student_name = request.POST.get('student')
#             parent_name = request.POST.get('parent')
#             student_contact = request.POST.get('student contact')
#             parent_contact = request.POST.get('parent contact')
#             amount = float(request.POST.get('amount', 0))
#             date_str = request.POST.get('date')
#             date = datetime.strptime(date_str, '%Y-%m-%d').date()
#             course = request.POST.get('course')

#             # Calculate installments
#             installment1_amount = round(amount / 2, 2)
#             installment2_amount = round(amount - installment1_amount, 2)  # Handles odd amounts
#             installment1_date = date
#             installment2_date = date + timedelta(days=30)  # Next installment after 30 days

#             # Create invoice
#             invoice = Invoice(
#                 date=date,
#                 installment1_amount=installment1_amount,
#                 installment1_date=installment1_date,
#                 installment2_amount=installment2_amount,
#                 installment2_date=installment2_date
#             )
#             invoice.save()

#             # Create invoice item
#             item = InvoiceItem(
#                 student_name=student_name,
#                 parent_name=parent_name,
#                 student_contact=student_contact,
#                 parent_contact=parent_contact,
#                 course=course,
#                 invoice=invoice,
#                 description=request.POST.get('description', 'No Description'),
#                 price=amount,
#                 quantity=1
#             )
#             item.save()

#             # Redirect to the billing page with invoice details
#             return redirect('bill_view', invoice_id=invoice.id)  # Redirect to bill_view

#         except Exception as e:
#             print(f"Error in gen_pdf: {str(e)}")
#             return redirect('billfrom')

# def bill_view(request, invoice_id):
#     try:
#         # Fetch the invoice details
#         invoice = Invoice.objects.get(id=invoice_id)
#         items = invoice.items.all()  # Fetch associated items using the related name
#         total = sum(item.total() for item in items)

#         # Extracting student and parent details from items
#         if items.exists():
#             student_name = items[0].student_name
#             parent_name = items[0].parent_name
#             student_contact = items[0].student_contact
#             parent_contact = items[0].parent_contact
#             course = items[0].course
#         else:
#             student_name = "N/A"
#             parent_name = "N/A"
#             student_contact = "N/A"
#             parent_contact = "N/A"
#             course = "N/A"

#         # Render the bill page with the invoice data
#         return render(request, 'bill.html', {
#             'invoice': invoice,
#             'items': items,
#             'total': total,
#             'student_name': student_name,
#             'parent_name': parent_name,
#             'student_contact': student_contact,
#             'parent_contact': parent_contact,
#             'course': course,
#         })
#     except Invoice.DoesNotExist:
#         return render(request, 'error.html', {'message': 'Invoice not found'})

# def print_invoice(request):
#     if request.method == 'POST':
#         data = request.POST

#         try:
#             printer = Network('192.168.1.100')  # Replace with your printer's IP address
#             printer.text('Invoice\n')
#             printer.text(f'Date: {data.get("date")}\n')

#             # Print invoice items
#             items = InvoiceItem.objects.filter(invoice_id=data.get("invoice_id"))
#             for item in items:
#                 printer.text(
#                     f'{item.student_name} ({item.student_contact}) - '
#                     f'{item.parent_name} ({item.parent_contact}): {item.course} '
#                     f'{item.description}: {item.quantity} x ₹{item.price}\n'
#                 )

#             # Calculate total and print
#             total = sum(item.price * item.quantity for item in items)
#             printer.text(f'Grand Total: ₹{total}\n')

#             # Print installment details
#             installment1_amount = data.get("installment1_amount")
#             installment1_date = data.get("installment1_date")
#             installment2_amount = data.get("installment2_amount")
#             installment2_date = data.get("installment2_date")
#             printer.text(
#                 f'Installment 1: ₹{installment1_amount} due by {installment1_date}\n'
#                 f'Installment 2: ₹{installment2_amount} due by {installment2_date}\n'
#             )

#             printer.cut()

#             return JsonResponse({'status': 'success', 'message': 'Print job sent to the printer.'})

#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': f'Error printing: {str(e)}'})

#     return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})



# # invoice_billing_app/views.py

# from django.shortcuts import render, redirect
# from .models import InvoiceItem, Invoice
# from django.http import JsonResponse
# from escpos.printer import Network
# from datetime import datetime, timedelta

# def index(request):
#     return render(request, 'index.html')

# def billform(request):
#     return render(request, 'billfrom.html')

# def gen_pdf(request):
#     if request.method == "POST":
#         try:
#             # Collect form data
#             student_name = request.POST.get('student')
#             parent_name = request.POST.get('parent')
#             student_contact = request.POST.get('student_contact')  # Use underscores in form field names
#             parent_contact = request.POST.get('parent_contact')
#             amount = float(request.POST.get('amount', 0))
#             date_str = request.POST.get('date')
#             date = datetime.strptime(date_str, '%Y-%m-%d').date()
#             course = request.POST.get('course')

#             # Calculate installments
#             installment1_amount = round(amount / 2, 2)
#             installment2_amount = round(amount - installment1_amount, 2)  # Handles odd amounts
#             installment1_date = date
#             installment2_date = date + timedelta(days=30)  # Next installment after 30 days

#             # Create invoice
#             invoice = Invoice(
#                 date=date,
#                 installment1_amount=installment1_amount,
#                 installment1_date=installment1_date,
#                 installment2_amount=installment2_amount,
#                 installment2_date=installment2_date
#             )
#             invoice.save()

#             # Create invoice item
#             item = InvoiceItem(
#                 student_name=student_name,
#                 parent_name=parent_name,
#                 student_contact=student_contact,
#                 parent_contact=parent_contact,
#                 course=course,
#                 invoice=invoice,
#                 description=request.POST.get('description', 'No Description'),
#                 price=amount,
#                 quantity=1
#             )
#             item.save()

#             # Redirect to the billing page with invoice details
#             return redirect('bill_view', invoice_id=invoice.id)  # Redirect to bill_view

#         except Exception as e:
#             print(f"Error in gen_pdf: {str(e)}")
#             return redirect('billform')

# def bill_view(request, invoice_id):
#     try:
#         # Fetch the invoice details
#         invoice = Invoice.objects.get(id=invoice_id)
#         items = invoice.items.all()  # Fetch associated items using the related name
#         total = sum(item.total() for item in items)

#         # Extracting student and parent details from items
#         if items.exists():
#             student_name = items[0].student_name
#             parent_name = items[0].parent_name
#             student_contact = items[0].student_contact
#             parent_contact = items[0].parent_contact
#             course = items[0].course
#         else:
#             student_name = "N/A"
#             parent_name = "N/A"
#             student_contact = "N/A"
#             parent_contact = "N/A"
#             course = "N/A"

#         # Render the bill page with the invoice data
#         return render(request, 'bill.html', {
#             'invoice': invoice,
#             'items': items,
#             'total': total,
#             'student_name': student_name,
#             'parent_name': parent_name,
#             'student_contact': student_contact,
#             'parent_contact': parent_contact,
#             'course': course,
#         })
#     except Invoice.DoesNotExist:
#         return render(request, 'error.html', {'message': 'Invoice not found'})

# def print_invoice(request):
#     if request.method == 'POST':
#         data = request.POST

#         try:
#             printer = Network('192.168.1.100')  # Replace with your printer's IP address
#             printer.text('Invoice\n')
#             printer.text(f'Date: {data.get("date")}\n')

#             # Print invoice items
#             items = InvoiceItem.objects.filter(invoice_id=data.get("invoice_id"))
#             for item in items:
#                 printer.text(
#                     f'{item.student_name} ({item.student_contact}) - '
#                     f'{item.parent_name} ({item.parent_contact}): {item.course} '
#                     f'{item.description}: {item.quantity} x ₹{item.price}\n'
#                 )

#             # Calculate total and print
#             total = sum(item.price * item.quantity for item in items)
#             printer.text(f'Grand Total: ₹{total}\n')

#             # Print installment details
#             installment1_amount = data.get("installment1_amount")
#             installment1_date = data.get("installment1_date")
#             installment2_amount = data.get("installment2_amount")
#             installment2_date = data.get("installment2_date")
#             printer.text(
#                 f'Installment 1: ₹{installment1_amount} due by {installment1_date}\n'
#                 f'Installment 2: ₹{installment2_amount} due by {installment2_date}\n'
#             )

#             printer.cut()

#             return JsonResponse({'status': 'success', 'message': 'Print job sent to the printer.'})

#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': f'Error printing: {str(e)}'})

#     return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
