from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views  # Import views directly from the current module

# Customize Django Admin Appearance
admin.site.site_header = "Star Mango Admin"
admin.site.site_title = "Star Mango Admin Portal"
admin.site.index_title = "Welcome to the Star Mango Admin Portal"

# ✅ Create a Proper Custom Admin Site
class CustomAdminSite(admin.AdminSite):
    """A custom admin panel where the dashboard is the default page."""
    site_header = "Star Mango Admin"
    site_title = "Star Mango Admin Portal"
    index_title = "Welcome to the Star Mango Admin Portal"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(views.dashboard), name='custom_admin_dashboard'),  # Dashboard as default
        ]
        return custom_urls + urls

# ✅ Register the custom admin site properly
custom_admin_site = CustomAdminSite(name="custom_admin")

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('inventory/', views.inventory_view, name='inventory'),
    path('sales/', views.sales_view, name='sales'),
    path('reports/', views.reports_view, name='reports'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    
    # Sales URLs
    path('sales/create/', views.create_sale, name='create_sale'),
    path('sales/<int:sale_id>/', views.view_sale, name='view_sale'),
    path('sales/<int:sale_id>/edit/', views.edit_sale, name='edit_sale'),
    path('sales/<int:sale_id>/delete/', views.delete_sale, name='delete_sale'),
    path('sales/<int:sale_id>/invoice/', views.generate_sales_invoice_pdf, name='generate_sales_invoice_pdf'),
    
    # Inventory URLs
    path('inventory/add/', views.add_inventory_item, name='add_inventory_item'),
    path('inventory/<int:item_id>/edit/', views.edit_inventory_item, name='edit_inventory_item'),
    path('inventory/<int:item_id>/delete/', views.delete_inventory_item, name='delete_inventory_item'),
]

