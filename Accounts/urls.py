from django.urls import path
from . import views  # Import views directly from the current module
from django.contrib import admin

# Customize the admin panel
admin.site.site_header = "Star Mango Admin"
admin.site.site_title = "Star Mango Admin Portal"
admin.site.index_title = "Welcome to the Star Mango Admin Portal"

# Create a custom admin site
class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(views.dashboard), name='custom_admin_dashboard'),  # Make dashboard the default admin view
        ]
        return custom_urls + urls

# Create and register the custom admin site
admin_site = CustomAdminSite(name='admin')
admin.site = admin_site

urlpatterns = [
    path('create-invoice/', views.create_invoice, name='create_invoice'),
    path('invoice/<int:invoice_id>/pdf/', views.generate_invoice_pdf, name='generate_invoice_pdf'),
    path('Accountvendor_summary/', views.vendor_summary, name='vendor_summary'),
    path('expense/<int:pk>/pdf/', views.generate_expense_pdf, name='generate_expense_pdf'),
    path('damage/<int:pk>/pdf/', views.generate_damage_pdf, name='generate_damage_pdf'),
    path('packaging_invoice/<int:invoice_id>/pdf/', views.generate_packaging_invoice_pdf, name='generate_packaging_pdf'),
    
    # New Frontend URLs
    path('', views.home, name='home'),
    path('inventory/', views.inventory_view, name='inventory'),
    path('inventory/add/', views.add_inventory_item, name='add_inventory_item'),
    path('inventory/edit/<int:item_id>/', views.edit_inventory_item, name='edit_inventory_item'),
    path('inventory/delete/<int:item_id>/', views.delete_inventory_item, name='delete_inventory_item'),
    path('sales/', views.sales_view, name='sales'),
    path('sales/new/', views.create_sale, name='create_sale'),
    path('sales/<int:sale_id>/', views.view_sale, name='view_sale'),
    path('sales/<int:sale_id>/print/', views.print_invoice, name='print_invoice'),
    path('reports/', views.reports_view, name='reports'),
    path('reports/sales/', views.export_sales_report, name='export_sales_report'),
    path('reports/inventory/', views.export_inventory_report, name='export_inventory_report'),
    path('reports/financial/', views.export_financial_report, name='export_financial_report'),
]
