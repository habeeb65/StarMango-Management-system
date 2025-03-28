from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views  # Import views directly from the current module

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('sales/', views.sales_view, name='sales'),
    path('reports/', views.reports_view, name='reports'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    
    # Sales URLs
    path('sales/<int:sale_id>/', views.view_sale, name='view_sale'),
    path('sales/<int:sale_id>/edit/', views.edit_sale, name='edit_sale'),
    path('sales/<int:sale_id>/delete/', views.delete_sale, name='delete_sale'),
    
    # Inventory URLs
    path('inventory/', views.inventory_view, name='inventory'),
    path('inventory/add/', views.add_inventory_item, name='add_inventory_item'),
    path('inventory/<int:item_id>/edit/', views.edit_inventory_item, name='edit_inventory_item'),
    path('inventory/<int:item_id>/delete/', views.delete_inventory_item, name='delete_inventory_item'),
]

