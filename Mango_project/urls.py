"""
URL configuration for Mango_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include 
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.conf.urls.static import static
from Accounts.views import generate_sales_invoice_pdf, home

def redirect_to_login(request):
    return redirect('login')

def redirect_to_accounts(request):
    return redirect('/accounts/login/')

urlpatterns = [
    path('', redirect_to_login),
    path('admin/', admin.site.urls),
    path('accounts/', include('Accounts.urls')),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('sales_invoice/<int:invoice_id>/pdf/', generate_sales_invoice_pdf, name='generate_sales_invoice_pdf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)




