from django.db import models
# borrowing the functionality of extending inbulit user from django
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.core.validators import RegexValidator
# Create your models here.

class Userprofile(AbstractUser):
    is_salesagent = models.BooleanField(null=False, default=False)
    is_manager = models.BooleanField(null=False, default=False)
    is_owner = models.BooleanField(null=False, default=False)
    username = models.CharField(max_length=50, unique=True, blank=False)
    branch_choices = (('Maganjo','Maganjo'), ('Matugga','Matugga'))
    branch = models.CharField(max_length=10, blank=False, choices=branch_choices)
    email = models.EmailField(max_length=100, unique=False)
    gender_choices = (('Female','Female'), ('Male','Male'))
    gender = models.CharField(max_length=10, blank=False, choices=gender_choices)
    phone = models.CharField(max_length=10, unique=False)
    address = models.CharField(max_length=100, blank=False)

    # this is to give the objects in the class Userprofile aname by which they are identified.
    def __str__(self):
        return self.username
    class Meta:
        db_table = 'userprofile'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Product(models.Model):
    product_name = models.CharField(max_length=100, blank=False, unique=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    product_description = models.TextField(blank=False)
    product_image = models.ImageField(upload_to='product_images', blank=True)
    product_category = models.CharField(max_length=100, blank=False)
    product_stock = models.IntegerField(blank=False)

    def __str__(self):
        return self.product_name
    class Meta:
        db_table = 'product'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

# getting the category for the particular stcock
class Category(models.Model):
    category_name=models.CharField(max_length=50, blank=True)
    def __str__(self):
        return self.category_name

class Stock(models.Model):
    # user_id=models.ForeignKey(Userprofile, on_delete=models.SET_NULL, null=True)
    
    Category_name= models.ForeignKey (Category, on_delete=models.CASCADE, blank=True)
    product_choices=(
        ('beans', 'beans'),
        ('soybeans', 'soybeans'),
        ('gnuts', 'gnuts'),
        ('maize', 'maize'),
        ('cowpeas', 'cowpeas'),
    )
    product_name = models.CharField(max_length=50, null=True, blank=True, choices=product_choices)
    total_quantity= models.PositiveIntegerField( default=0, blank=True, null=True)
    issued_quantity= models.PositiveIntegerField(default=0, blank=True, null=True)
    received_quantity= models.PositiveIntegerField( default=0, blank=True, null=True)
    cost_of_stock= models.DecimalField(max_digits=50, blank=True, null=True, default=1000000, decimal_places=0)
    unit_cost= models.IntegerField(blank=True, null=True, default=500)
    unit_price= models.IntegerField(blank=True, null=True, default=500)  
    date_of_stock= models.DateField(auto_now_add=True ,blank=True, null=True)
    supplier_name= models.CharField(max_length=100)
    type_of_stock = models.CharField(max_length=100, blank=True, null=True)
    entry_agent= models.ForeignKey(Userprofile, on_delete=models.SET_NULL, null=True, blank=True)
    

    def __str__ (self):
        return self.product_name

class Sale(models.Model):
    
    product_name= models.ForeignKey(Stock, on_delete=models.CASCADE,max_length=100, blank=True, null=True)
    unit_price= models.IntegerField( blank=False, null=True, default=100.0)
    quantity= models.IntegerField( blank=True, default=0, null=True)
    customer_name= models.CharField(max_length=100, blank=False, null=True)
    date= models.DateField(auto_now_add=True, blank=False, null=True)
    amount_received= models.IntegerField( blank=False, default=1500, null=True)
    payment_method_choices=(
        ('Cash', 'Cash'),
        ('Credit', 'Credit'),
        ('Debit', 'Debit'),
        ('Mobile Money', 'Mobile Money'),
        ('Bank Transfer', 'Bank Transfer'),
    )
    payment_method= models.CharField(max_length=50, choices=payment_method_choices, blank=False, null=True)
    sales_agent= models.ForeignKey(Userprofile,on_delete=models.CASCADE, blank=True)

    def total_sale(self):
        total= self.quantity * self.product_name.unit_price
        """if self.product_name and self.product_name .unit_price is not None:
            return self.quantity * self.product_name.unit_price"""
        return total
    # calculating the total sale of the product sold
    
    def get_change(self):
        amount_received = self.amount_received
        total = self.total_sale()
        change = amount_received - total
        return change

    def __str__ (self):
        return self.customer_name
    
# Model for Credit Sale
class CreditSale(models.Model):
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE)
    
    customer_name = models.CharField(max_length=100)
    national_id = models.CharField(max_length=20)
    phone_regex = RegexValidator(
        regex=r'^\+?256[0-9]{9,15}$',
        message="Phone number must be in the format: '+2567XXXXXXXX'.")
    contact = models.CharField(max_length=15, validators=[phone_regex], blank=False)
    location = models.CharField(max_length=100)
    due_date = models.DateField()
    amount_due = models.IntegerField( blank=False, default=10000)

    def __str__(self):
        return f"Credit Sale to {self.buyer_name} for {self.sale.product.product_name}"
    