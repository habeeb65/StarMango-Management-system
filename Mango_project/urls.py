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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView, LogoutView

# Set Admin appearance with standard Django admin only
admin.site.site_header = "Star Mango Admin"
admin.site.site_title = "Star Mango Admin Portal"
admin.site.index_title = "Welcome to the Star Mango Admin Portal"

urlpatterns = [
    # Use the standard Django admin only
    path('admin/', admin.site.urls),
    
    # Include Accounts app URLs with proper namespace
    path('accounts/', include('Accounts.urls')),
    
    # Authentication URLs
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    # Redirect root to accounts home
    path('', lambda request: redirect('home')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Add this if you need to serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




