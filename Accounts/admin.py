from django.contrib import admin
from .models import *

# Register models with the standard admin site only
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(PurchaseVendor)
admin.site.register(PurchaseInvoice)
admin.site.register(SalesInvoice)
admin.site.register(Expense)
admin.site.register(Damages)
admin.site.register(Packaging_Invoice)
# Add other models as needed
