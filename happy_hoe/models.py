from django.db import models
# borrowing the functionality of extending inbulit user from django
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
from django.core.cache import cache
from django.core.validators import RegexValidator
# Create your models here.
class Branch(models.Model):
    branch_name= models.CharField(max_length=20, default="", blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, unique=True)
    location = models.CharField(max_length=50, default="", blank=True, null=True)

    # Get all stock items for this branch
    def get_branch_stock(self):
        
        return self.stock_set.all()

    # Get all sales for this branch
    def get_branch_sales(self):
        
        return Sale.objects.filter(sales_agent__branch=self)

    #  Get all users assigned to this branch
    def get_branch_users(self):
       
        return self.userprofile_set.all()


    def get_director(self):
        return self.userprofile_set.count()


    def get_manager(self):
        return self.userprofile_set.filter(is_manager=True).first()

    def get_sales_agents(self):
        return self.userprofile_set.filter(is_salesagent=True)

   
    def __str__(self):
        return self.branch_name

    class Meta:
        verbose_name_plural = 'Branches'


class Userprofile(AbstractUser):
    is_salesagent = models.BooleanField(null=True, default=True)
    is_manager = models.BooleanField(null=True, default=True)
    is_director = models.BooleanField(null=True, default=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    is_online = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=(
            ('online', 'Online'),
            ('offline', 'Offline'),
           
        ),
        default='offline'
    )

    username = models.CharField(max_length=50, unique=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE,max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True)
    gender_choices = (('Female','Female'), ('Male','Male'))
    gender = models.CharField(max_length=10, blank=True, choices=gender_choices)
    phone = models.CharField(max_length=10, unique=True)
    address = models.CharField(max_length=100, blank=True)
    status = models

    def update_online_status(self):
        now = timezone.now()
        # Consider user offline if last activity was more than 5 minutes ago
        if (now - self.last_activity).seconds > 300:
            self.is_online = True
            self.status = 'offline'
        else:
            self.is_online = True
            self.status = 'online'
        self.save()
   
    
    def clean(self):
    # Ensure a branch has only one manager
        if self.is_manager:
            existing_manager = Userprofile.objects.filter(
                branch=self.branch, 
                is_manager=True
            ).exclude(pk=self.pk).exists()
            if existing_manager:
                raise ValidationError("This branch already has a manager.")

        """ # Ensure user has only one role
        roles = [self.is_manager, self.is_salesagent, self.is_director, self]
        if sum(roles) > 1:
            raise ValidationError("A user can only have one role.")"""

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
     # this is to give the objects in the class Userprofile aname that i can use to identify them.
    def __str__(self):
        return self.username
    
    
    class Meta:
        db_table = 'userprofile'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


# getting the category for the particular stcock
class Category(models.Model):
    category_name=models.CharField(max_length=50, null=False, blank=False, default='')
    description=models.TextField(max_length=50, blank=False, default='')
    def __str__(self):
        return self.category_name

class Produce(models.Model):
    branch= models.ForeignKey(Branch, on_delete=models.CASCADE,blank=True, null=True)
    product_name = models.CharField(max_length=20, blank=True, unique=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    product_description = models.TextField(blank=True)
    product_image = models.ImageField(upload_to='product_images', blank=True)
    product_category = models.CharField(max_length=100, blank=True)
    product_stock = models.IntegerField(blank=True)

    def __str__(self):
        return self.product_name
    class Meta:
        db_table = 'produce'
        verbose_name = 'Produce'
        verbose_name_plural = 'Produce'





class Stock(models.Model):
    # user_id=models.ForeignKey(Userprofile, on_delete=models.SET_NULL, null=True)
    branch= models.ForeignKey(Branch, on_delete=models.CASCADE,  related_name='branch_stock', null=True, blank=True)
    Category_name= models.ForeignKey (Category, on_delete=models.CASCADE, blank=True)
    product_choices=(
        ('beans', 'beans'),
        ('soybeans', 'soybeans'),
        ('gnuts', 'gnuts'),
        ('maize', 'maize'),
        ('cowpeas', 'cowpeas'),
    )
    product_name = models.CharField(max_length=50, null=True, blank=False, choices=product_choices)
    total_quantity= models.PositiveIntegerField( default=0, blank=False, null=False)
    issued_quantity= models.PositiveIntegerField(default=0, blank=True, null=False)
    received_quantity= models.PositiveIntegerField( default=0, blank=False, null=False)
    cost_of_stock= models.DecimalField(max_digits=50, blank=False, null=False, default=1000000, decimal_places=0)
    unit_cost= models.IntegerField(blank=False, null=False, default=500)
    unit_price= models.IntegerField(blank=True, null=True, default=500)  
    date_of_stock= models.DateField(auto_now_add=True ,blank=False, null=True)
    supplier_name= models.CharField(max_length=100, blank=False, null=False)
    phone_regex = RegexValidator(
        regex=r'^\+?256[0-9]{9,15}$',
        message="Phone number must be in the format: '+2567XXXXXXXX'.")
    supplier_contact = models.CharField(max_length=15, validators=[phone_regex], blank=False, null=True)
    
    type_of_produce = models.CharField(max_length=100, blank=False, null=True)
    entry_agent= models.ForeignKey(Userprofile, on_delete=models.CASCADE, null=False, blank=False, related_name='stocks_entered')
    

    def __str__(self):
        return f"{self.product_name} - {self.branch.branch_name}"
    
    class Meta:
        # Add constraints for data integrity
        constraints = [
            models.UniqueConstraint(
                fields=['branch', 'product_name'], 
                name='unique_product_per_branch'
            )
        ]
        indexes = [
            models.Index(fields=['branch', 'product_name']),
        ]
        ordering = ['branch', 'product_name']

    def clean(self):
        # Validate that stock entry agent belongs to same branch
        if self.entry_agent and self.entry_agent.branch != self.branch:
            raise ValidationError("Entry agent must belong to the same branch")


class Sale(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='branch_sales', null=True, blank=True)
    product_name= models.ForeignKey(Stock, on_delete=models.CASCADE,max_length=100, blank=True, null=True)
    unit_price= models.IntegerField( blank=False, null=False, default=1000)
    quantity= models.IntegerField( blank=False, default=5, null=False)
    customer_name= models.CharField(max_length=100, blank=True, null=True)
    date= models.DateField(auto_now_add=True, blank=True, null=True)
    amount_received= models.IntegerField( blank=True, default=1500, null=True)
    payment_method_choices=(
        ('Cash', 'Cash'),
        ('Credit', 'Credit'),
        ('Mobile Money', 'Mobile Money'),
        
    )
    payment_method= models.CharField(max_length=50, choices=payment_method_choices, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('PAID', 'Paid'),
            ('PENDING', 'Pending'),
            ('CANCELLED', 'Cancelled')
        ],
        default='PAID'
    )
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
    
    # making the string representation to include branch
    def __str__(self):
        
        return f"{self.customer_name} - {self.branch.branch_name}"

    
    class Meta:
        # Add constraints and indexes for better performance
        indexes = [
            models.Index(fields=['branch', 'date']),
        ]
        # Optional: Ensure each branch's sales are grouped together
        ordering = ['branch', '-date']

    def save(self, *args, **kwargs):
        # Ensure sale is associated with sales agent's branch
        if not self.branch_id and self.sales_agent:
            self.branch = self.sales_agent.branch
        super().save(*args, **kwargs)

    def clean(self):
        # Validate that sale belongs to same branch as the stock and sales agent
        if self.sales_agent and self.sales_agent.branch != self.branch:
            raise ValidationError("Sales agent must belong to the same branch as the sale")
        if self.product_name and self.product_name.branch != self.branch:
            raise ValidationError("Product must belong to the same branch as the sale")

# Model for Credit Sale
class CreditSale(models.Model):
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, related_name='credit_details', null=True, blank=True)
    
    customer_name = models.CharField(max_length=100)
    national_id = models.CharField(max_length=20, blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r'^\+?256[0-9]{9,15}$',
        message="Phone number must be in the format: '+2567XXXXXXXX'.")
    contact = models.CharField(max_length=15, validators=[phone_regex], blank=True, null=True)
    location = models.CharField(max_length=100)
    due_date = models.DateField()
    amount_paid = models.IntegerField(max_length=10, default=10000)
    balance = models.IntegerField(max_length=10, null=True, blank=True, default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('PAID', 'Paid'),
            ('OVERDUE', 'Overdue')
        ],
        default='PENDING'
    )

    def __str__(self):
        return f"{self.customer_name} - {self.sale.product_name} ({self.sale.branch.branch_name})"
    
    def clean(self):
        if self.amount_paid > self.sale.total_sale():
            raise ValidationError("Amount paid cannot exceed total sale amount")
        self.balance = self.sale.total_sale() - self.amount_paid
    
    