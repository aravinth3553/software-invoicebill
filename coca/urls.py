# from django.urls import path
# from . import views
# from django.conf import settings
# from django.conf.urls.static import static


# urlpatterns = [
#     path('', views.index, name='index'),  # Home page
#     path('generate/', views.gen_pdf, name='gen_pdf'),  # Generate invoice PDF
#     path('bill/<int:invoice_id>/', views.bill, name='bill'),  # View billing details (with invoice ID)
#     path('print_invoice/', views.print_invoice, name='print_invoice'),  # Print invoice
#     path('bill_view/<int:invoice_id>/', views.bill_view, name='bill_view'),  # Bill page (latest invoice)
    
# ]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


 
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('billfrom/', views.billform, name='billfrom'),  # Home page
    path('generate/', views.gen_pdf, name='gen_pdf'),  # Generate invoice PDF
    path('bill/<int:invoice_id>/', views.bill_view, name='bill_view'),  # View billing details (with invoice ID)
    path('print_invoice/', views.print_invoice, name='print_invoice'),  # Print invoice
    path('software/',views.software,name='software'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


