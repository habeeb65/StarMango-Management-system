from django.db import models
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.contrib.auth.models import User

class PurchaseVendor(models.Model):
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    area = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('account_pay', 'Account Pay'),
        ('upi', 'UPI GPay / PhonePay'),
        ('cash', 'Cash'),
    ]
    invoice = models.ForeignKey('PurchaseInvoice', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date = models.DateField(default=date.today)
    # New field: Payment mode as a drop-down
    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash',  # You can set a default or remove default if needed
        verbose_name="Payment Method"
    )
    
    # New field: Attachment for screenshot/reference
    attachment = models.FileField(
        upload_to='payment_attachments/', 
        blank=True, 
        null=True,
        verbose_name="Payment Attachment"
    )

    def clean(self):
        invoice = self.invoice
        # Calculate the total of all payments for this invoice excluding the current instance if it exists.
        if self.pk:
            # Existing payment: exclude self from the total.
            current_total = invoice.payments.exclude(pk=self.pk).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        else:
            # New payment: there is no current value.
            current_total = Decimal('0')
            
        # Calculate what the new total would be after this payment is added/updated.
        new_total = current_total + self.amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        net_total_after_cash_cutting = invoice.net_total_after_cash_cutting

        if new_total > net_total_after_cash_cutting:
            raise ValidationError(
                f"Total payment cannot exceed the net total after 2% cash cutting: ₹{net_total_after_cash_cutting}."
            )
                
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment of ₹{self.amount} for Invoice {self.invoice.invoice_number}"


class PurchaseInvoice(models.Model):
    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    lot_number = models.CharField(max_length=10, unique=True, editable=False)
    date = models.DateField(default=date.today)
    vendor = models.ForeignKey('PurchaseVendor', on_delete=models.CASCADE, related_name='invoices')
    net_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_issuer_name = models.CharField(
        max_length=100,
        choices=[('Abdul Rafi', 'Abdul Rafi'), ('Sadiq', 'Sadiq')],
        blank=True,
        null=True
    )
    
    def save(self, *args, **kwargs):
        # --- Generate invoice_number if not set (only for new objects) ---
        if not self.invoice_number and self.pk is None:
            last_invoice = PurchaseInvoice.objects.order_by("-id").first()
            if last_invoice and last_invoice.invoice_number:
                try:
                    # Extract the last two digits and increment
                    last_number = int(last_invoice.invoice_number[-2:])
                except ValueError:
                    last_number = 0
                self.invoice_number = f"MS2025R{last_number + 1:02d}"
            else:
                self.invoice_number = "MS2025R01"  # Default starting number

        # --- Generate lot_number if not set (only for new objects) ---
        if not self.lot_number and self.pk is None:
            last_lot = PurchaseInvoice.objects.order_by("-id").first()
            if last_lot and last_lot.lot_number:
                try:
                    last_lot_number = int(last_lot.lot_number.split("-")[-1])
                except ValueError:
                    last_lot_number = 0
                self.lot_number = f"LOT-{last_lot_number + 1:02d}"
            else:
                self.lot_number = "LOT-01"  # Default starting lot number

        # --- First save to ensure the instance gets a primary key ---
        super().save(*args, **kwargs)

        # --- Update net_total after saving ---
        calculated_total = sum(product.total for product in self.purchase_products.all())
        if self.net_total != calculated_total:
            self.net_total = calculated_total
            # Update only the net_total field
            super().save(update_fields=["net_total"])

    @property
    def available_quantity(self):
        # Existing purchased quantity
        total_purchased = sum(product.quantity for product in self.purchase_products.all())
        
        # Sum of quantities used in ALL sales invoices
        total_used = self.sales_lots.aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        
        return total_purchased - total_used      

    @property
    def net_total_after_cash_cutting(self):
        # Calculate net total after deducting 2%
        return round(self.net_total - (self.net_total * Decimal('0.02')), 2)

    @property
    def paid_amount(self):
        return round(sum(payment.amount for payment in self.payments.all()), 2)

    @property
    def due_amount(self):
        return round(self.net_total_after_cash_cutting - self.paid_amount, 2)
    
    #@property
    # def available_quantity(self):
    #     # Sum of quantities purchased from all products in this invoice.
    #     total_purchased = sum(product.quantity for product in self.purchase_products.all())
    #     # Sum of quantities already sold from this lot in all sales invoices.
    #     total_sold = self.sales_invoices.aggregate(total=Sum('lot_quantity'))['total'] or 0
    #     return total_purchased - total_sold

    def __str__(self):
        return (
            #f"Invoice {self.invoice_number} - Net Total: ₹{self.net_total}, "
            #f"Net Total After Cash Cutting: ₹{self.net_total_after_cash_cutting}, "
            #f"Paid Amount: ₹{self.paid_amount}, Due Amount: ₹{self.due_amount}"
            f" {self.lot_number} (Invoice {self.invoice_number})"
        )

    def get_product_quantities(self):
        products = {}
        for purchase_product in self.purchase_products.all():
            sold = SalesProduct.objects.filter(
                invoice__lot=self,
                product=purchase_product.product
            ).aggregate(total=Sum('quantity'))['total'] or 0
            available = purchase_product.quantity - sold
            products[purchase_product.product.name] = available
        return products
    class Meta:
        verbose_name = "Lot"
        verbose_name = "Purchase Invoice"  # Singular name
        verbose_name_plural = "Purchase Invoices"  # Plural name
class Purchase(models.Model):
    invoice = models.OneToOneField(PurchaseInvoice, on_delete=models.CASCADE, related_name='purchase_invoice')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total_amount = sum(product.total for product in self.invoice.purchase_products.all())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Purchase for Invoice {self.invoice.invoice_number}"


class Product(models.Model):
    name = models.CharField(max_length=100)
   
    current_stock = models.IntegerField(default=0)  # ✅ Ensure this field exists
    threshold = models.IntegerField(default=5)  # ✅ Ensure this field exists

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class PurchaseProduct(models.Model):
    invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE, related_name='purchase_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    serial_number = models.IntegerField(default=0, editable=False)  # Make it non-editable
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    damage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rotten = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    loading_unloading = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Add this

    def save(self, *args, **kwargs):
    # Auto-generate serial_number if not set (only for new objects)
        if not self.serial_number and self.pk is None:
            last_product = PurchaseProduct.objects.filter(invoice=self.invoice).order_by('-serial_number').first()
            if last_product:
                self.serial_number = last_product.serial_number + 1
            else:
                self.serial_number = 1  # Start from 1 for the first product in the invoice

    # Calculate total
        discount_quantity = (self.quantity * self.discount) / 100
        damage_quantity = (self.quantity * self.damage) / 100
        remaining_quantity = self.quantity - discount_quantity - damage_quantity - self.rotten

        # Calculate loading/unloading cost (0.40 per unit of quantity)
        self.loading_unloading = Decimal(self.quantity) * Decimal('0.40')

        # Calculate total (price * remaining quantity after all deductions + loading/unloading cost)
        self.total = (remaining_quantity * self.price) - self.loading_unloading

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} in Invoice {self.invoice.invoice_number}"


class SalesInvoice(models.Model):
    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    vendor = models.ForeignKey('Customer', on_delete=models.PROTECT, related_name='sales_invoices')
    
    lots = models.ManyToManyField(
        'PurchaseInvoice',
        through='SalesLot',
        verbose_name="Lots Used",
        help_text="Select multiple lots and specify quantities used"
    )
    # Lot info from a Purchase Invoice.
    # This field lets you select a lot (from a purchase invoice) for sale.
    #lot = models.ForeignKey(
    #     'PurchaseInvoice',
    #     on_delete=models.SET_NULL,
    #     related_name='sales_invoices',
    #     blank=True,
    #     null=True,
    #     help_text="Select a lot from a Purchase Invoice. (When used, mark as Sold.)"
    # )
    
    # Record how much (in weight) from the lot is used for this sale.
    # lot_quantity = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
    #                                    help_text="Quantity (in kgs) used from the selected lot.")
    
    date = models.DateField(default=date.today)
    vehicle_number = models.CharField(max_length=50, blank=True, null=True)
    gross_vehicle_weight = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                               help_text="In Kilograms")
    reference = models.CharField(max_length=200, blank=True, null=True)
    
    # Packaging & Loading Cost fields
    no_of_crates = models.IntegerField(blank=True, null=True)
    cost_per_crate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    
    def save(self, *args, **kwargs):
        # Auto-generate invoice number if not set.
        if not self.invoice_number and self.pk is None:
            last_invoice = SalesInvoice.objects.order_by("-id").first()
            if last_invoice and last_invoice.invoice_number:
                try:
                    last_number = int(last_invoice.invoice_number[-2:])
                except ValueError:
                    last_number = 0
                self.invoice_number = f"SA2025S{last_number + 1:02d}"
            else:
                self.invoice_number = "SA2025S01"
        super().save(*args, **kwargs)
    
    # Computed properties for totals:
    @property
    def total_gross_weight(self):
        """Sum of gross weights of all sales products."""
        total = self.sales_products.aggregate(total=models.Sum('gross_weight'))['total'] or Decimal('0.00')
        return total
    
    @property
    def net_total(self):
        """Sum of all line item totals."""
        total = self.sales_products.aggregate(total=models.Sum('total'))['total'] or Decimal('0.00')
        return total
    
    @property
    def net_total_after_commission(self):
        """
        Net Total After Commission = Net Total + Total Gross Weight
        (For example, commission might be structured as a fixed addition per kg.)
        """
        return self.net_total + self.total_gross_weight
    
    @property
    def packaging_total(self):
        """Packaging and Loading cost = no_of_crates * cost_per_crate."""
        # Check if both no_of_crates and cost_per_crate are not None
        if self.no_of_crates is not None and self.cost_per_crate is not None:
            # Return the total cost by multiplying no_of_crates and cost_per_crate
            return Decimal(self.no_of_crates) * self.cost_per_crate
        # Return 0.00 if either no_of_crates or cost_per_crate is None
        return Decimal('0.00')
    
    @property
    def net_total_after_packaging(self):
        """
        Final invoice total = Net Total After Commission + Packaging Total.
        """
        return self.net_total_after_commission + self.packaging_total
    
    @property
    def paid_amount(self):
        """Sum of all related payments"""
        return self.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    @property
    def due_amount(self):
        """Remaining balance"""
        return self.net_total_after_packaging - self.paid_amount

    def payment_status(self):
        """Payment status indicator"""
        if self.due_amount == 0:
            return "Paid"
        elif self.paid_amount == 0:
            return "Unpaid"
        return "Partial"

    def __str__(self):
        return f"Sales Invoice {self.invoice_number} for {self.vendor}"


# -------------------------------------------
# Sales Product Model (Line Items)
# -------------------------------------------
class SalesProduct(models.Model):
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE, related_name='sales_products')
    serial_number = models.IntegerField(editable=False)  # Auto-incremented within the invoice
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    
    # We store the weights in kilograms
    gross_weight = models.DecimalField(max_digits=12, decimal_places=2, help_text="Gross Weight in Kgs")
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                   help_text="Discount as percentage")
    rotten = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                 help_text="Rotten weight in Kgs")
    # These fields are computed:
    net_weight = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                     help_text="Net Weight in Kgs after discount & rotten deduction")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                help_text="Total = Net Weight * Price")
    
    def save(self, *args, **kwargs):
        # Auto-generate serial_number if not set.
        if not self.serial_number:
            last_item = SalesProduct.objects.filter(invoice=self.invoice).order_by('-serial_number').first()
            self.serial_number = last_item.serial_number + 1 if last_item else 1
        
        # Calculate net_weight:
        # net_weight = gross_weight - (gross_weight * discount/100) - rotten
        self.net_weight = self.gross_weight - ((self.gross_weight * self.discount) / Decimal('100.00')) - self.rotten
        # Calculate total:
        self.total = self.net_weight * self.price
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.serial_number}. {self.product.name} in Invoice {self.invoice.invoice_number}"

    lot = models.ForeignKey(
        'SalesLot',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Link to specific lot usage"
    )
# -------------------------------------------
# Sales Payment Model
# -------------------------------------------
class SalesPayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('account_pay', 'Account Pay'),
        ('upi', 'UPI GPay / PhonePay'),
        ('cash', 'Cash'),
    ]
    
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date = models.DateField(default=date.today)
    payment_mode = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES, 
        default='cash', 
        verbose_name="Payment Method"
    )
    attachment = models.FileField(
        upload_to='sales_payment_attachments/', 
        blank=True, 
        null=True,
        verbose_name="Payment Attachment"
    )
    
    def __str__(self):
        return f"Payment of ₹{self.amount} for Sales Invoice {self.invoice.invoice_number}"
    
class Customer(models.Model):
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
class Expense(models.Model):
    date = models.DateField()
    paid_by = models.CharField(max_length=100)
    paid_to = models.CharField(max_length=100)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.date} - {self.paid_to} - ₹{self.amount}"
class Damages(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=100)
    due_to = models.CharField(max_length=100)
    description = models.TextField()
    amount_loss = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.date} - {self.due_to} - ₹{self.amount_loss}"
    class Meta:
        verbose_name = "Damage"  # Singular form
        verbose_name_plural = "Damages"  # Explicitly set plural name

class SalesLot(models.Model):
    """Tracks which lots (from purchase invoices) are used in a sales invoice"""
    sales_invoice = models.ForeignKey(
        'SalesInvoice', 
        on_delete=models.CASCADE,
        related_name='sales_lots'
    )
    purchase_invoice = models.ForeignKey(
        'PurchaseInvoice',
        on_delete=models.CASCADE,
        related_name='sales_lots',
        verbose_name="Lot"
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Quantity used from this lot (in kgs)"
    )

    class Meta:
        unique_together = ('sales_invoice', 'purchase_invoice')  # Prevent duplicates

    def __str__(self):
        return f"{self.quantity}kg from {self.purchase_invoice.lot_number}"
    
    def clean(self):
        super().clean()
        
        # Check available quantity
        if self.quantity > self.purchase_invoice.available_quantity:
            raise ValidationError(
                f"Only {self.purchase_invoice.available_quantity}kg available in {self.purchase_invoice.lot_number}"
            )

        # Skip product check if SalesInvoice is unsaved (no primary key)
        if not self.sales_invoice.pk:
            return  # Skip validation until parent is saved

        # Check product consistency (only after SalesInvoice is saved)
        sales_products = self.sales_invoice.sales_products.all()
        if sales_products.exists():
            sales_product = sales_products.first().product
            if not self.purchase_invoice.purchase_products.filter(product=sales_product).exists():
                raise ValidationError(
                    f"Lot {self.purchase_invoice.lot_number} doesn't contain {sales_product.name}"
            )
class Packaging_Invoice(models.Model):
    no_of_crates = models.IntegerField(blank=True, null=True)
    cost_per_crate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    @property
    def packaging_total(self):
        """Packaging and Loading cost = no_of_crates * cost_per_crate."""
        # Check if both no_of_crates and cost_per_crate are not None
        if self.no_of_crates is not None and self.cost_per_crate is not None:
            # Return the total cost by multiplying no_of_crates and cost_per_crate
            return Decimal(self.no_of_crates) * self.cost_per_crate
        # Return 0.00 if either no_of_crates or cost_per_crate is None
        return Decimal('0.00')