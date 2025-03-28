from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, LongTable
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from django.conf import settings
from .models import PurchaseInvoice, PurchaseVendor, SalesInvoice, Expense, Damages, Packaging_Invoice, Customer, PurchaseProduct, Product, Category
from decimal import Decimal
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
from reportlab.lib.units import inch
from reportlab.platypus import Frame
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles.finders import find
import base64
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, F
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import UserCreationForm


@staff_member_required
def home(request):
    # Get statistics for home page
    total_inventory = Product.objects.count()
    total_sales = SalesInvoice.objects.count()
    total_customers = Customer.objects.count()
    
    # Calculate total revenue from sales
    total_revenue = SalesInvoice.objects.aggregate(
        total=Sum('net_total_after_packaging')
    )['total'] or 0
    
    # Get recent sales (last 5)
    recent_sales = SalesInvoice.objects.select_related('vendor').order_by('-date')[:5]
    
    # Get low stock items
    low_stock_items = Product.objects.filter(current_stock__lte=F('threshold'))
    
    context = {
        "total_inventory": total_inventory,
        "total_sales": total_sales,
        "total_customers": total_customers,
        "total_revenue": total_revenue,
        "recent_sales": recent_sales,
        "low_stock_items": low_stock_items,
    }
    return render(request, 'home.html', context)

@login_required
def inventory_view(request):
    # Get inventory items with pagination
    inventory_items = Product.objects.select_related('category').all().order_by('name')
    categories = Category.objects.all()
    
    # Get statistics
    total_products = inventory_items.count()
    low_stock_items = inventory_items.filter(current_stock__lte=F('threshold'))
    
    context = {
        'inventory_items': inventory_items,
        'categories': categories,
        'total_products': total_products,
        'low_stock_items': low_stock_items,
    }
    return render(request, 'inventory.html', context)

@login_required
def sales_view(request):
    # Get all sales with related vendor info
    sales = SalesInvoice.objects.select_related('vendor').order_by('-date')
    
    # Calculate today's sales
    today = timezone.now().date()
    today_sales = SalesInvoice.objects.filter(date=today).annotate(
        total=Sum('sales_products__total')
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Get total sales for statistics using sales_products__total
    total_sales = SalesInvoice.objects.annotate(
        sale_total=Sum('sales_products__total')
    ).aggregate(
        total=Sum('sale_total')
    )['total'] or 0
    
    # Get recent sales for quick view
    recent_sales = sales[:10]
    
    # Get vendors for sale creation
    vendors = PurchaseVendor.objects.all()
    
    # Get products for sale creation
    products = Product.objects.filter(current_stock__gt=0)

    context = {
        'sales': sales,
        'today_sales': today_sales,
        'total_sales': total_sales,
        'recent_sales': recent_sales,
        'vendors': vendors,
        'products': products,
    }
    return render(request, 'sales.html', context)

@login_required
def reports_view(request):
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Base queryset for sales and purchases
    sales_query = SalesInvoice.objects.all()
    purchases_query = PurchaseInvoice.objects.all()
    
    # Apply date filters if provided
    if start_date:
        sales_query = sales_query.filter(date__gte=start_date)
        purchases_query = purchases_query.filter(date__gte=start_date)
    if end_date:
        sales_query = sales_query.filter(date__lte=end_date)
        purchases_query = purchases_query.filter(date__lte=end_date)
    
    # Get total sales using sales_products__total
    total_sales = sales_query.annotate(
        sale_total=Sum('sales_products__total')
    ).aggregate(
        total=Sum('sale_total')
    )['total'] or 0
    
    # Get total purchases
    total_purchases = purchases_query.aggregate(
        total=Sum('net_total')
    )['total'] or 0
    
    # Get total expenses and damages
    expenses_query = Expense.objects.all()
    damages_query = Damages.objects.all()
    
    if start_date:
        expenses_query = expenses_query.filter(date__gte=start_date)
        damages_query = damages_query.filter(date__gte=start_date)
    if end_date:
        expenses_query = expenses_query.filter(date__lte=end_date)
        damages_query = damages_query.filter(date__lte=end_date)
    
    total_expenses = expenses_query.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    total_damages = damages_query.aggregate(
        total=Sum('amount_loss')
    )['total'] or 0
    
    # Get recent sales and purchases
    recent_sales = sales_query.select_related('vendor').order_by('-date')[:10]
    recent_purchases = purchases_query.select_related('vendor').order_by('-date')[:10]
    
    # Get inventory status data
    inventory_data = {
        'in_stock': Product.objects.filter(current_stock__gt=F('threshold')).count(),
        'low_stock': Product.objects.filter(current_stock__lte=F('threshold'), current_stock__gt=0).count(),
        'out_of_stock': Product.objects.filter(current_stock=0).count()
    }
    
    # Get payment methods distribution
    # Since payment_method doesn't exist in SalesInvoice, we'll need to adapt this
    # For now, we'll use a placeholder with fixed values
    payment_methods = ['Cash', 'Card', 'UPI', 'Bank Transfer']
    payment_data = []
    for method in payment_methods:
        # Instead of filtering by payment_method, we'll just count all sales
        # This is a placeholder - you'll need to adjust based on your actual data model
        count = sales_query.count() // len(payment_methods)  # Distribute evenly for now
        payment_data.append({
            'method': method,
            'count': count
        })
    
    # Get top selling products
    top_products = Product.objects.annotate(
        total_quantity=Sum('salesproduct__net_weight'),
        total_revenue=Sum('salesproduct__total')
    ).filter(total_quantity__gt=0).order_by('-total_quantity')[:5]
    
    # Calculate profit/loss
    total_profit = total_sales - (total_purchases + total_expenses + total_damages)
    
    context = {
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'total_expenses': total_expenses,
        'total_damages': total_damages,
        'total_profit': total_profit,
        'recent_sales': recent_sales,
        'recent_purchases': recent_purchases,
        'inventory_data': inventory_data,
        'payment_methods': payment_methods,
        'payment_data': payment_data,
        'top_products': top_products,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'reports.html', context)


# Font and Logo Setup
FONT_PATH = os.path.join(os.path.dirname(__file__), 'Font', 'DejaVuSans.ttf')
BOLD_FONT_PATH = os.path.join(os.path.dirname(__file__), 'Font', 'DejaVuSans-Bold.ttf')
FONT_PATH = os.path.join(os.path.dirname(__file__), 'Font', 'NotoSans.ttf')
BOLD_FONT_PATH = os.path.join(os.path.dirname(__file__), 'Font', 'NotoSans-Bold.ttf')
pdfmetrics.registerFont(TTFont('DejaVuSans', FONT_PATH))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', BOLD_FONT_PATH))
pdfmetrics.registerFont(TTFont('NotoSans', FONT_PATH))
pdfmetrics.registerFont(TTFont('NotoSans-Bold', BOLD_FONT_PATH))

def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:image/png;base64,{encoded_string}"

def create_invoice(request):
    return render(request, 'Accounts/create_invoice.html')

def generate_invoice_pdf(request, invoice_id):
    # Fetch invoice
    invoice = get_object_or_404(PurchaseInvoice, id=invoice_id)

    # Set up PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="invoice_{invoice.invoice_number}.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=20, bottomMargin=30)

    elements = []  # Correct indentation here

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=16, alignment=1, textColor=colors.black)

    # Add Title
    elements.append(Paragraph("PURCHASE INVOICE", title_style))

    # Add logo
    logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'LOGO.png')  # Ensure the path is correct
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2*inch, height=1.5*inch)  # Adjust size as needed
        logo.hAlign = 'CENTER'  # Align the logo to the center of its cell
    else:
        print(f"Logo file not found at {logo_path}")

    # Add Vendor Info Table with yellow highlights
    vendor_data = [
        ["Name:", invoice.vendor.name, "DATE", invoice.date.strftime('%d-%m-%Y')],
        ["Contact No:", invoice.vendor.contact_number, "INVOICE NO.", invoice.invoice_number],
        ["Area:", invoice.vendor.area, "LOT NO.", invoice.lot_number],
        
    ]
    vendor_table = Table(vendor_data, colWidths=[1*inch, 2*inch, 1*inch, 1.15*inch])
    vendor_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # Grid lines for table
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Align text to the left
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),  # Font for the table
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size
        ('BACKGROUND', (0, 0), (0, 0), colors.yellow),  # Highlight "Name:" in yellow
        ('BACKGROUND', (0, 1), (0, 1), colors.yellow),  # Highlight "Contact No:" in yellow
        ('BACKGROUND', (0, 2), (0, 2), colors.yellow),  # Highlight "Area:" in yellow
        ('BACKGROUND', (2, 0), (2, 0), colors.yellow),  # Highlight "DATE" in yellow
        ('BACKGROUND', (2, 1), (2, 1), colors.yellow),  # Highlight "INVOICE NO." in yellow
        ('BACKGROUND', (2, 2), (2, 2), colors.yellow),  # Highlight "LOT NO." in yellow
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Black text for headers
    ]))

    # Create a new table to place the logo and vendor info side by side
    side_by_side_table = Table([[logo, vendor_table]], colWidths=[2.5*inch, 5*inch])  # Adjust widths as needed

    # Add the side-by-side table to the elements list
    elements.append(side_by_side_table)
    elements.append(Spacer(1, 20))  # Add space after the logo and table

    

    # Product Table with yellow header
    product_data = [
        ["S/No", "Product Name", "QTY in Kg's", "UNIT PRICE", "Damage", "Discount", "Rotten", "Unloading", "TOTAL"]
    ]
    for idx, product in enumerate(invoice.purchase_products.all(), start=1):
        product_data.append([
            idx, product.product.name, f"{product.quantity:.2f}", f"₹{product.price:.2f}",
            f"{product.damage:.2f}%", f"{product.discount:.2f}%", f"{product.rotten:.2f}",
            f"₹{product.loading_unloading:.2f}", f"₹{product.total:.2f}"
        ])
    product_table = LongTable(product_data, colWidths=[0.4*inch, 1.5*inch, 0.8*inch, 0.8*inch, 1*inch, 0.8*inch, 0.8*inch, 1*inch, 0.9*inch])
    product_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.yellow),  # Yellow background for header
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Black text for header
    ]))
    elements.append(product_table)
    elements.append(Spacer(1, 20))

    # Paid Amounts Section
    paid_data = [["Paid Amount", "Date"]]
    for payment in invoice.payments.all():  # Assuming 'payments' is a related name for payments in the PurchaseInvoice model
        paid_data.append([f"₹{payment.amount:.2f}", payment.date.strftime('%Y-%m-%d')])

    paid_data.append(["Total Paid:", f"₹{invoice.paid_amount:.2f}"])

    paid_table = Table(paid_data, colWidths=[2*inch, 1.8*inch])
    paid_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('BACKGROUND', (0, 0), (0, 0), colors.yellow),  # Yellow header for "Paid Amount" and "Date"
        ('FONTNAME', (0, -1), (-1, -1), 'DejaVuSans-Bold'),  # Bold for Total Paid row
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Black text for header
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTSIZE', (0, -1), (-1, -1), 12),  # Larger font for Total Paid
    ]))
    
    # Payment Summary with yellow highlighting
    payment_data = [
        ["NET TOTAL", f"₹{invoice.net_total:.2f}"],
        ["2% CASH COMMISSION", f"₹{(invoice.net_total * Decimal('0.02')):.2f}"],
        ["NET TOTAL AFTER CASH CUTTING", f"₹{invoice.net_total_after_cash_cutting:.2f}"],
        ["TOTAL PAID", f"₹{invoice.paid_amount:.2f}"],
        ["BALANCE DUE", f"₹{invoice.due_amount:.2f}"],
    ]
    

    payment_table = Table(payment_data, colWidths=[2.5*inch, 1.4*inch])
    payment_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTNAME', (0, -1), (-1, -1), 'DejaVuSans-Bold'),  
    

        ('BACKGROUND', (0, 0), (-1, 0), colors.yellow),  # Yellow background for the header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Black text for header
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    
    #elements.append(payment_table)
    paid_and_payment_table = Table(
        [[paid_table, payment_table]],  # Add both tables as cells in a single row
        colWidths=[4*inch, 4*inch]  # Adjust column widths as needed
    )

    

    # Add the combined table to the elements list
    elements.append(paid_and_payment_table)
    elements.append(Spacer(1, 20))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    response.write(buffer.read())
    return response

def vendor_summary(request):
    vendors = PurchaseVendor.objects.all()
    selected_vendor_id = request.GET.get('vendor_id')
    year = request.GET.get('year')
    purchases = []
    total_amount = 0

    if selected_vendor_id:
        purchases = PurchaseInvoice.objects.filter(vendor_id=selected_vendor_id)
        if year:
            purchases = purchases.filter(date__year=year)  # Extract the year from the date field
            total_amount = purchases.aggregate(Sum('net_total'))['net_total__sum'] or 0

    context = {
        'vendors': vendors,
        'purchases': purchases,
        'total_amount': total_amount,
        'selected_vendor_id': selected_vendor_id,
        'year': year,
    }
    return render(request, 'vendor_summary.html', context)

def generate_sales_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(SalesInvoice, id=invoice_id)
    # Check if "hide_payments" parameter exists in the URL
    hide_payments = request.GET.get('hide_payments', False)
    # Set up PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="sales_invoice_{invoice.invoice_number}.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=30
    )

    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=16,
                                 alignment=1, textColor=colors.black)

    

    # Add Title
    elements.append(Paragraph("SALES INVOICE", title_style))
    elements.append(Spacer(1, 12))

    # Add logo
    # Logo and Header Section
    logo_header_table = []

    # Add Logo (if available)
    logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'LOGO.png')  # Updated path
    if os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=2*inch, height=1.5*inch)
            logo.hAlign = 'CENTER'
            # Create a logo cell with proper padding
            logo_cell = [[logo]]
            logo_table = Table(logo_cell, hAlign='LEFT')
            logo_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
            ]))
            logo_header_table.append(logo_table)
        except Exception as e:
            print(f"Error loading logo: {str(e)}")
    else:
        print(f"Logo file not found at {logo_path}")

    # Create header table
    header_data = [
        ["",""],
        [ "Invoice Number:", invoice.invoice_number, "Date:", invoice.date.strftime('%d-%m-%Y')],
        ["Vendor Name:", invoice.vendor.name,],
        ["Contact No:", invoice.vendor.contact_number or "N/A", "Vehicle No.", invoice.vehicle_number or "N/A" ],
        [ "Reference", invoice.reference or "", "Gross Vehicle Weight:", f"{invoice.gross_vehicle_weight}"],
        ["LOT NO:", ", ".join([sl.purchase_invoice.lot_number for sl in invoice.sales_lots.all()]) or "N/A", "", ""],
    ]

    header_table = Table(header_data, colWidths=[1.25*inch, 1.5*inch, 1.75*inch, 1.5*inch])
    header_table.setStyle(TableStyle([
      
        
        ('SPAN', (1, 5), (3, 5)),  # (col_start, row_start), (col_end, row_end)
        ('SPAN', (1, 2), (3, 2)),  # (col_start, row_start), (col_end, row_end)
    # Align LOT NO text to the left
        ('ALIGN', (1, 5), (3, 5), 'LEFT'),
        ('GRID', (0,1), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (2,1), (3,-1), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (3,-1), 'Helvetica-Bold'),
        ('ALIGN', (2,1), (3,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0, 1), (0, 1), colors.yellow), 
        ('BACKGROUND', (0, 2), (0, 2), colors.yellow), 
        ('BACKGROUND', (0, 3), (0, 3), colors.yellow), 
        ('BACKGROUND', (0, 4), (0, 4), colors.yellow),
        ('BACKGROUND', (2, 1), (2, 1), colors.yellow), 
        ('BACKGROUND', (2, 3), (2, 3), colors.yellow), 
       
        ('BACKGROUND', (2, 4), (2, 4), colors.yellow),
        ('BACKGROUND', (0, 5), (0, 5), colors.yellow),
    ]))

    # Combine logo and header into a single row
    if logo_header_table:
        final_header = [[logo_header_table[0], header_table]]
        col_widths = [2.5*inch, 6.5*inch]
    else:
        final_header = [[header_table]]
        col_widths = [8.5*inch]

    main_header = Table(final_header, colWidths=col_widths)
    main_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))

    elements.append(main_header)
    elements.append(Spacer(1, 20))

    # Sales Product Table - Improved layout
    product_header = [
        "S/No", "Product", "Gross Weight", "Net Weight", 
        "Price/Kg", "Discount", "Rotten", "Total"
    ]
    product_data = [product_header]
    
    for idx, sp in enumerate(invoice.sales_products.all(), start=1):
        product_data.append([
            str(idx),
            sp.product.name,
            f"{sp.gross_weight:.2f} Kg",
            f"{sp.net_weight:.2f} Kg",
            f"₹ {sp.price:.2f}",
            f"{sp.discount:.2f}%",
            f"{sp.rotten:.2f} Kg",
            f"₹{sp.total:.2f}"
        ])
    
    product_table = Table(product_data, 
                         colWidths=[0.4*inch, 1.8*inch, 1*inch, 1*inch, 
                                   0.9*inch, 0.8*inch, 0.9*inch, 1.2*inch])
    
    product_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.yellow),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
    ]))
    
    elements.append(product_table)
    elements.append(Spacer(1, 20))

    # Enhanced Summary Section
    summary_data = [
        ["Total Gross Weight:", f"{invoice.total_gross_weight:.2f} Kg"],
        ["Net Total:", f"₹{invoice.net_total:.2f}"],
        ["Commission:", f"₹{invoice.net_total_after_commission - invoice.net_total:.2f}"],
        ["Net Total After Commission:", f"₹{invoice.net_total_after_commission:.2f}"],
        ["Number of Crates:", f"{invoice.no_of_crates or 0}"],
        ["Cost Per Crate:", f"₹{invoice.cost_per_crate or 0:.2f}"],
        ["Packaging & Loading Cost:", f"₹{invoice.packaging_total:.2f}"],
        ["Final Total:", f"₹{invoice.net_total_after_packaging:.2f}"]
        #["TOTAL PAID", f"₹{invoice.paid_amount:.2f}"],
        #["BALANCE DUE", f"₹{invoice.due_amount:.2f}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTNAME', (0, 0), (0, -1), 'DejaVuSans-Bold'),
        ('BACKGROUND', (0, 0), (0, 0), colors.yellow),
        ('BACKGROUND', (0, 0), (0, 1), colors.yellow),
        ('BACKGROUND', (0, 0), (0, 2), colors.yellow),
        ('BACKGROUND', (0, 0), (0, 3), colors.yellow),
        ('BACKGROUND', (0, 0), (0, 4), colors.yellow),
        ('BACKGROUND', (0, 0), (0, 5), colors.yellow),
        ('BACKGROUND', (0, 0), (0, 6), colors.yellow),
        ('BACKGROUND', (0, 0), (0, 7), colors.yellow),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
         ('FONTSIZE', (0, 7), (0, 7), 14),
         ('FONTSIZE', (1, 7), (1, 7), 14),
         ('FONTNAME', (1, 7), (1, 7), 'DejaVuSans-Bold'),
        ('TEXTCOLOR', (0, -1), (0, -1), colors.black),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
    ]))
    
    left_aligned_summary = Table([[summary_table]], colWidths=[4*inch])
    left_aligned_summary.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 140),
    ]))

    elements.append(left_aligned_summary)
    elements.append(Spacer(1, 25))
    if not hide_payments:
    # Payment Details Section
    # Payment Details Section - Updated to match purchase invoice style
        paid_data = [["Paid Amount", "Date"]]
        for payment in invoice.payments.all():
            paid_data.append([f"₹{payment.amount:.2f}", payment.date.strftime('%Y-%m-%d')])
        paid_data.append(["Total Paid:", f"₹{invoice.paid_amount:.2f}"])

        paid_table = Table(paid_data, colWidths=[2*inch, 1.8*inch])
        paid_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('BACKGROUND', (0, 0), (0, 0), colors.yellow),
            ('BACKGROUND', (1, 0), (1, 0), colors.yellow),
            ('FONTNAME', (0, -1), (-1, -1), 'DejaVuSans-Bold'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
        ]))

        # Payment Summary Table with yellow highlights
        payment_summary_data = [
            ["NET TOTAL", f"₹{invoice.net_total_after_packaging:.2f}"],
            ["TOTAL PAID", f"₹{invoice.paid_amount:.2f}"],
            ["BALANCE DUE", f"₹{invoice.due_amount:.2f}"],
        ]
        
        payment_summary_table = Table(payment_summary_data, colWidths=[2.5*inch, 1.4*inch])
        payment_summary_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTNAME', (0, -1), (-1, -1), 'DejaVuSans-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.yellow),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))

        # Combine payment tables side by side
        combined_payments = Table([[paid_table, payment_summary_table]],
                                colWidths=[4*inch, 4*inch])
        
        elements.append(combined_payments)
        elements.append(Spacer(1, 20))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    response.write(buffer.read())
    return response

def generate_expense_pdf(request, pk):
    expense = Expense.objects.get(pk=pk)

    # Get static files paths for fonts
    font_normal = find('NotoSans.ttf')
    font_bold = find('NotoSans-Bold.ttf')

    # Get the logo path (ensure it exists!)
    logo_file_path = find('LOGO.png')

    if not logo_file_path:
        raise FileNotFoundError("LOGO.png not found in static files!")

    # Base64 encode the logo
    logo_base64 = get_base64_image(logo_file_path)

    # Fix path for fonts
    def fix_path(path):
        return path.replace('\\', '/') if os.name == 'nt' else path

    context = {
        'expense': expense,
        'logo_path': logo_base64,  # Base64 encoded image for embedding
        'noto_sans_path': f"file://{fix_path(font_normal)}" if font_normal else '',
        'noto_sans_bold_path': f"file://{fix_path(font_bold)}" if font_bold else ''
    }

    return render_to_pdf('expense_pdf.html', context)


def generate_damage_pdf(request, pk):
    damage = Damages.objects.get(pk=pk)

    # Get static files paths for fonts
    font_normal = find('NotoSans.ttf')
    font_bold = find('NotoSans-Bold.ttf')

    # Get the logo path (ensure it exists!)
    logo_file_path = find('LOGO.png')

    if not logo_file_path:
        raise FileNotFoundError("LOGO.png not found in static files!")

    # Base64 encode the logo
    logo_base64 = get_base64_image(logo_file_path)

    # Fix path for fonts
    def fix_path(path):
        return path.replace('\\', '/') if os.name == 'nt' else path

    context = {
        'damage': damage,
        'logo_path': logo_base64,  # Base64 encoded image for embedding
        'noto_sans_path': f"file://{fix_path(font_normal)}" if font_normal else '',
        'noto_sans_bold_path': f"file://{fix_path(font_bold)}" if font_bold else ''
    }

    return render_to_pdf('damage_pdf.html', context)

# Generic PDF renderer (reuse existing if you have one)
def render_to_pdf(template_path, context):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="document.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(
        html, dest=response,
        encoding='UTF-8'
    )

    if pisa_status.err:
        return HttpResponse('Error generating PDF')
    return response

def generate_packaging_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Packaging_Invoice, id=invoice_id)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="packaging_invoice_{invoice.id}.pdf"'
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                          rightMargin=20, leftMargin=20,
                          topMargin=20, bottomMargin=30)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom style with DejaVu font
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=16,
        alignment=1,
        textColor=colors.black,
        fontName='DejaVuSans-Bold'
    )
    
    # Add Logo and Header
    logo_header = []
    logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'LOGO.png')
    
    if os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=2*inch, height=1.5*inch)
            logo.hAlign = 'LEFT'
            logo_table = Table([[logo]], colWidths=[2*inch])
            logo_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'LEFT'),
                ('LEFTPADDING', (0,0), (-1,-1), -50),
            ]))
            logo_header.append(logo_table)
        except Exception as e:
            print(f"Error loading logo: {str(e)}")
    
    # Create header table
    header_data = [
        ["PACKAGING INVOICE", ""],
        ["Invoice ID:", f"PKG-{invoice.id}"],  # Using invoice ID instead of date
    ]
    
    header_table = Table(header_data, colWidths=[3*inch, 3*inch])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'DejaVuSans'),
        ('FONTSIZE', (0,0), (-1,0), 14),
        ('FONTNAME', (0,0), (-1,0), 'DejaVuSans-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    # Combine logo and header
    if logo_header:
        main_header = Table([[logo_header[0], header_table]], 
                          colWidths=[2*inch, 4*inch])
    else:
        main_header = header_table
        
    elements.append(main_header)
    elements.append(Spacer(1, 20))
    
    invoice_data = [
        ["Number of Crates:", str(invoice.no_of_crates)],
        ["Cost Per Crate:", f"₹{invoice.cost_per_crate:.2f}"],
        ["Total Packaging Cost:", f"₹{invoice.packaging_total:.2f}"]
    ]
    
    invoice_table = Table(invoice_data, colWidths=[2*inch, 4*inch])
    invoice_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'DejaVuSans'),
        ('BACKGROUND', (0,0), (-1,0), colors.yellow),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    elements.append(invoice_table)
    elements.append(Spacer(1, 20))
    
    # Footer with custom font
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.darkgrey,
        fontName='DejaVuSans'
    )
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.darkgrey
    )
    footer_text = '''<para>
    Prepared By: _______________________ &nbsp;&nbsp;&nbsp;&nbsp; 
    Approved By: _______________________<br/>
    Signature: _______________________ &nbsp;&nbsp;&nbsp;&nbsp; 
    Signature: _______________________
    </para>'''
    
    elements.append(Paragraph(footer_text, footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    response.write(buffer.read())
    buffer.close()
    return response

@login_required
def home(request):
    # Get total products
    total_products = Product.objects.count()
    
    # Get total sales (using sales_products total)
    total_sales = SalesInvoice.objects.annotate(
        total=Sum('sales_products__total')
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Get total vendors
    total_vendors = PurchaseVendor.objects.count()
    
    # Get today's sales (fixed date lookup)
    today = timezone.now().date()
    today_sales = SalesInvoice.objects.filter(date=today).annotate(
        total=Sum('sales_products__total')
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Get recent sales
    recent_sales = SalesInvoice.objects.select_related('vendor').order_by('-date')[:5]
    
    # Get low stock products (using threshold)
    low_stock_products = Product.objects.filter(current_stock__lte=F('threshold'))[:5]
    
    context = {
        'total_products': total_products,
        'total_sales': total_sales,
        'total_vendors': total_vendors,
        'today_sales': today_sales,
        'recent_sales': recent_sales,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'base.html', context)

def inventory_view(request):
    """Inventory management view"""
    # Get filter parameters
    search = request.GET.get('search', '')
    category_id = request.GET.get('category')
    stock_status = request.GET.get('stock_status')
    
    # Base queryset
    items = Product.objects.select_related('category')
    
    # Apply filters
    if search:
        items = items.filter(name__icontains=search)
    if category_id:
        items = items.filter(category_id=category_id)
    if stock_status == 'low':
        items = items.filter(current_stock__lte=F('min_stock'))
    elif stock_status == 'out':
        items = items.filter(current_stock=0)
    elif stock_status == 'in':
        items = items.filter(current_stock__gt=F('min_stock'))
    
    # Pagination
    paginator = Paginator(items, 10)
    page = request.GET.get('page')
    inventory_items = paginator.get_page(page)
    
    # Get categories for filter
    categories = Category.objects.all()
    
    context = {
        'inventory_items': inventory_items,
        'categories': categories,
    }
    return render(request, 'inventory.html', context)

@login_required
def add_inventory_item(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        current_stock = request.POST.get('current_stock')
        threshold = request.POST.get('threshold')
        
        Product.objects.create(
            name=name,
            category_id=category_id,
            price=price,
            current_stock=current_stock,
            threshold=threshold
        )
        messages.success(request, 'Product added successfully!')
        return redirect('inventory')
    
    categories = Category.objects.all()
    return render(request, 'add_inventory_item.html', {'categories': categories})

@login_required
def edit_inventory_item(request, item_id):
    item = get_object_or_404(Product, id=item_id)
    
    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.category_id = request.POST.get('category')
        item.price = request.POST.get('price')
        item.current_stock = request.POST.get('current_stock')
        item.threshold = request.POST.get('threshold')
        item.save()
        
        messages.success(request, 'Product updated successfully!')
        return redirect('inventory')
    
    categories = Category.objects.all()
    return render(request, 'edit_inventory_item.html', {'item': item, 'categories': categories})

@login_required
def delete_inventory_item(request, item_id):
    item = get_object_or_404(Product, id=item_id)
    item.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('inventory')

@login_required
def create_sale(request):
    if request.method == 'POST':
        # Handle sale creation
        vendor_id = request.POST.get('vendor')
        products = request.POST.getlist('products[]')
        quantities = request.POST.getlist('quantities[]')
        
        try:
            vendor = PurchaseVendor.objects.get(id=vendor_id)
            sale = SalesInvoice.objects.create(
                vendor=vendor,
                date=timezone.now(),
                payment_status='pending'
            )
            
            total = 0
            for product_id, quantity in zip(products, quantities):
                product = Product.objects.get(id=product_id)
                price = product.selling_price
                item_total = price * int(quantity)
                total += item_total
                
                SalesProduct.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    price=price,
                    total=item_total
                )
                
                # Update product stock
                product.current_stock -= int(quantity)
                product.save()
            
            sale.net_total = total
            sale.save()
            
            messages.success(request, 'Sale created successfully!')
            return redirect('view_sale', sale_id=sale.id)
            
        except Exception as e:
            messages.error(request, f'Error creating sale: {str(e)}')
            return redirect('sales')
    
    vendors = PurchaseVendor.objects.all()
    products = Product.objects.filter(current_stock__gt=0)
    context = {
        'vendors': vendors,
        'products': products,
    }
    return render(request, 'create_sale.html', context)

@login_required
def view_sale(request, sale_id):
    sale = get_object_or_404(SalesInvoice.objects.select_related('vendor'), id=sale_id)
    sale_products = sale.sales_products.select_related('product').all()
    
    context = {
        'sale': sale,
        'sale_products': sale_products,
    }
    return render(request, 'view_sale.html', context)

def export_sales_report(request):
    """Export sales report"""
    # Implementation for sales report export
    pass

def export_inventory_report(request):
    """Export inventory report"""
    # Implementation for inventory report export
    pass

def export_financial_report(request):
    """Export financial report"""
    # Implementation for financial report export
    pass

# Add the missing print_invoice view
def print_invoice(request, sale_id):
    """
    Render a printer-friendly version of a sales invoice.
    This view prepares a sales invoice for printing.
    """
    sale = get_object_or_404(SalesInvoice, id=sale_id)
    context = {
        'sale': sale,
        'products': sale.sales_products.all().order_by('serial_number'),
        'lots': sale.sales_lots.all(),
        'payments': sale.payments.all(),
        'print_mode': True,
    }
    return render(request, 'Accounts/print_invoice.html', context)

def is_admin(user):
    return user.is_staff

@login_required
def dashboard_view(request):
    # Calculate total sales by summing up the sales_products totals
    total_sales = SalesInvoice.objects.annotate(
        sale_total=Sum('sales_products__total')
    ).aggregate(
        total=Sum('sale_total')
    )['total'] or 0
    
    # Calculate total purchases
    total_purchases = PurchaseInvoice.objects.aggregate(
        total=Sum('net_total')
    )['total'] or 0
    
    # Get total expenses and damages
    total_expenses = Expense.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    total_damages = Damages.objects.aggregate(
        total=Sum('amount_loss')
    )['total'] or 0
    
    # Get recent sales and purchases with related vendor info
    recent_sales = SalesInvoice.objects.select_related('vendor').order_by('-date')[:5]
    
    # Calculate totals for each sale to avoid using template filter
    sales_with_totals = []
    for sale in recent_sales:
        # Calculate the total for this sale
        sale_total = sale.sales_products.aggregate(total=Sum('total'))['total'] or 0
        sales_with_totals.append({
            'sale': sale,
            'total': sale_total
        })
    
    # Get recent purchases
    recent_purchases = PurchaseInvoice.objects.select_related('vendor').order_by('-date')[:5]
    
    # Get inventory status data
    inventory_data = {
        'in_stock': Product.objects.filter(current_stock__gt=F('threshold')).count(),
        'low_stock': Product.objects.filter(current_stock__lte=F('threshold'), current_stock__gt=0).count(),
        'out_of_stock': Product.objects.filter(current_stock=0).count()
    }
    
    # Get top selling products - using correct field relationships
    # We need to use the right field from the SalesProduct model
    top_products = Product.objects.annotate(
        total_quantity=Sum('salesproduct__net_weight'),
        total_revenue=Sum('salesproduct__total')
    ).filter(total_quantity__gt=0).order_by('-total_quantity')[:5]
    
    context = {
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'total_expenses': total_expenses,
        'total_damages': total_damages,
        'recent_sales': recent_sales,
        'sales_with_totals': sales_with_totals,
        'recent_purchases': recent_purchases,
        'inventory_data': inventory_data,
        'top_products': top_products,
    }
    return render(request, 'dashboard.html', context)

@login_required
def edit_sale(request, sale_id):
    sale = get_object_or_404(SalesInvoice.objects.select_related('vendor'), id=sale_id)
    
    if request.method == 'POST':
        try:
            # Update sale details
            vendor_id = request.POST.get('vendor')
            vehicle_number = request.POST.get('vehicle_number')
            reference = request.POST.get('reference')
            gross_vehicle_weight = request.POST.get('gross_vehicle_weight')
            
            # Update basic sale information
            sale.vendor_id = vendor_id
            sale.vehicle_number = vehicle_number
            sale.reference = reference
            sale.gross_vehicle_weight = gross_vehicle_weight
            
            # Update products
            products = request.POST.getlist('products[]')
            gross_weights = request.POST.getlist('gross_weights[]')
            net_weights = request.POST.getlist('net_weights[]')
            prices = request.POST.getlist('prices[]')
            discounts = request.POST.getlist('discounts[]')
            rottens = request.POST.getlist('rottens[]')
            
            # Clear existing products
            sale.sales_products.all().delete()
            
            # Add new products
            total = 0
            for i in range(len(products)):
                product = Product.objects.get(id=products[i])
                gross_weight = Decimal(gross_weights[i])
                net_weight = Decimal(net_weights[i])
                price = Decimal(prices[i])
                discount = Decimal(discounts[i])
                rotten = Decimal(rottens[i])
                
                # Calculate total for this product
                product_total = (net_weight * price) * (1 - discount/100)
                total += product_total
                
                # Create new sales product
                sale.sales_products.create(
                    product=product,
                    gross_weight=gross_weight,
                    net_weight=net_weight,
                    price=price,
                    discount=discount,
                    rotten=rotten,
                    total=product_total
                )
            
            # Update sale totals
            sale.net_total = total
            sale.net_total_after_commission = total * Decimal('1.10')  # 10% commission
            sale.save()
            
            messages.success(request, 'Sale updated successfully!')
            return redirect('view_sale', sale_id=sale.id)
            
        except Exception as e:
            messages.error(request, f'Error updating sale: {str(e)}')
            return redirect('edit_sale', sale_id=sale.id)
    
    # GET request - show edit form
    vendors = PurchaseVendor.objects.all()
    products = Product.objects.all()
    sale_products = sale.sales_products.select_related('product').all()
    
    context = {
        'sale': sale,
        'vendors': vendors,
        'products': products,
        'sale_products': sale_products,
    }
    return render(request, 'edit_sale.html', context)

@login_required
def delete_sale(request, sale_id):
    sale = get_object_or_404(SalesInvoice, id=sale_id)
    
    try:
        # Get all products from the sale
        sale_products = sale.sales_products.all()
        
        # Restore product quantities back to inventory
        for sale_product in sale_products:
            product = sale_product.product
            product.current_stock += sale_product.net_weight
            product.save()
        
        # Delete the sale
        sale.delete()
        messages.success(request, 'Sale deleted successfully!')
        
    except Exception as e:
        messages.error(request, f'Error deleting sale: {str(e)}')
    
    return redirect('sales')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Check if the user should be admin (staff)
            if request.POST.get('is_staff'):
                user.is_staff = True
                user.save()
                
            messages.success(request, 'Account created successfully! You can now login.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})