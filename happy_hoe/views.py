from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.contrib import messages
# Create your views here.
from .models import *
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import *
# borrowing decorators for authentication
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserCreation

from django.db.models import Sum, F, FloatField
from django.db.models.functions import Coalesce
import json
from django.core.serializers.json import DjangoJSONEncoder
 
@login_required
def all_branches(request):
    branches = Branch.objects.all()
    return render(request, 'happy_hoeapp/branch.html', {'branches': branches})



@login_required
def add_branch(request):
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branch created successfully!')
            return redirect('branches_list')
    else:
        form = BranchForm()
    return render(request, 'happy_hoeapp/add_branch.html', {'form': form})


@login_required
def all_users(request):
    # excluding the superuser
    users = Userprofile.objects.exclude(is_superuser=True).order_by('-date_joined')
    
    # Get counts for different user types
    total_users = users.count()
    total_managers = users.filter(is_manager=True).count()
    total_salesagents = users.filter(is_salesagent=True).count()
    
    context = {
        'users': users,
        'total_users': total_users,
        'total_managers': total_managers,
        'total_salesagents': total_salesagents,
        'title': 'Users Management'
    }
    
    return render(request, 'happy_hoeapp/users.html', context)

def stock_detail(request, stock_id):
    stock = Stock.objects.get(id=stock_id)

    return render(request, 'fooapp/detail.html', {'stock': stock})



@login_required
@user_passes_test(lambda u: u.is_director)
def edit_branch(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branch updated successfully!')
            return redirect('all_branches')
    else:
        form = BranchForm(instance=branch)
    return render(request, 'happy_hoeapp/edit_branch.html', {'form': form, 'branch': branch})

@login_required
@user_passes_test(lambda u: u.is_director)
def delete_branch(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    if request.method == 'POST':
        branch.delete()
        messages.success(request, 'Branch deleted successfully!')
        return redirect('all_branches')
    return redirect('all_branches')

# view for the index page
def index(request):
    context = {
        "site_name": "Kgl management system",       
        "products": ["G'nuts", "Beans", "Maize", "soybeans", "cowpeas"],
    }
    # getting all the registered stock from our data base
    stocks=Stock.objects.all().order_by('-id')

    return render(request,"happy_hoeapp/index.html", {"stocks": stocks})

def categories(request):
    categories = Category.objects.all().order_by('-id')
    if request.method == 'POST':
        data = request.POST
        try:
            category = Category.objects.create(
                category_name=data.get('category_name'),
                description=data.get('description')
            )
            messages.success(request, f'Category "{category.category_name}" added successfully!')
            return redirect('categories')
        except Exception as e:
            messages.error(request, f'Error adding category: {str(e)}')
    
    return render(request, "happy_hoeapp/category.html", {'categories': categories})
# view for deleting category
def delete_category(request, pk):
    category = get_object_or_404(Category, id=pk)
    if request.method == 'POST':
        category_name = category.category_name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('categories')
    return render(request, "happy_hoeapp/delete_category.html", {'category': category})

# view for editting the category
def edit_category(request, pk):
    try:
        category = get_object_or_404(Category, id=pk)
        
        if request.method == 'POST':
            category.category_name = request.POST.get('category_name')
            category.description = request.POST.get('description')
            category.save()
            messages.success(request, f'Category "{category.category_name}" updated successfully!')
            return redirect('categories')
            
        return render(request, 'happy_hoeapp/edit_category.html', {
            'category': category
        })
    except Exception as e:
        messages.error(request, f'Error updating category: {str(e)}')
        return redirect('categories')

#  view for the add_stock
def add_stock(request, pk):
    issued_item = Stock.objects.get(id=pk)
    form = UpdateStockForm(request.POST )
    if request.method == 'POST':
        if form.is_valid():
            # creating a new stock object and saving it to the database
            added_quantity = int(request.POST['received_quantity'])
            issued_item.total_quantity += added_quantity
            issued_item.save()
    
            # to add to the remaining stock quantity is increasing
            print(added_quantity)
            print(issued_item.total_quantity)
            return redirect('index')
    
    return render(request,"happy_hoeapp/add_stock.html", {"form": form})

#  view for the allstock
def Procurement(request):
    if request.method=='POST':
        data=request.POST
        #new_amount = int(sent_amount) / 3670
        procurement= Stock(**{
            "Category_name": data.get('Category_name'),
            "product_name":data.get('product_name'),
            "tota_quantity":data.get('total_quantity'),
            "received_quantity":data.get('received_quantity'),
            "cost_of_stock":data.get('cost_of_stock'),
            "unit_cost":data.get('unit_cost'),
            "unit_price":data.get('unit_price'),
            "date_of_stock": data.get('date_of_stock'),
            "supplier_name": data.get('supplier_name'),
            "type_of_stock":data.get('type_of_stock'),
            "entry_agent":data.get('entry_agent'),


        })

        procurement.save()
        messages.succes(request, 'Stock addded successfully!')
        return redirect ('index')
    
    
    return render(request,"happy_hoeapp/procurement.html")

#  view for the addsale
def add_sale(request):
    return render(request,"happy_hoeapp/add_sale.html")
#  view for the addstock
def creditsale(request):
    return render(request,"happy_hoeapp/creditsale.html")


#  view for the all_sales
def all_sales(request):
    return render(request,"happy_hoeapp/all_sales.html")

#  view for the receipt

def sales(request):
    # getting all the registered sales from our data base
    sales=Sale.objects.all().order_by('-id')
    return render(request,"happy_hoeapp/transactions.html", {"sales": sales})

# aview to handle a link to handle a particular item for a sale
def stock_detail(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    if stock.branch != request.user.branch and not request.user.is_superuser:
        raise "PermissionDenied"
    return render(request, 'happy_hoeapp/detail.html', {'stock': stock})
def issue_item(request,pk):
    # creating a variable issued item and acces all entries in the stock model by their models 
    issued_item=Stock.objects.get(id=pk)
    # acccessing our form from forms.py
    sales_form = AddSaleForm(request.POST)
    if request.method == 'POST':
        if sales_form.is_valid():
            new_sale = sales_form.save(commit = False)
            # the new_sale.(...) if followed by the propeerty that represents the sale
            new_sale.product_name = issued_item 
            new_sale.unit_price = issued_item.unit_price
            new_sale.save()
            # to keep track of the stock remaining after sale
            issued_quantity = int(request.POST['quantity'])
            issued_item.total_quantity -= issued_quantity
            issued_item.save()
            print(issued_item.product_name)
            print(request.POST['quantity'])
            print(issued_item.total_quantity)
            return redirect ('sales')
    return render(request, 'happy_hoeapp/issue_item.html', {
        'sales_form': sales_form,
        'issued_item': issued_item
    })

def receipt_detail(request, receipt_id):
    receipt = Sale.objects.get(id=receipt_id)
    return render(request, 'happy_hoeapp/final_receipt.html', {'receipt': receipt})

def receipt(request):
    # getting all the registered sales from our data base
    sales=Sale.objects.all().order_by('-id')
    return render(request,"happy_hoeapp/receipt.html", {"sales": sales})
#  view for the login page
def Login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password =request.POST.get('password')
        # ckecking the logging in user
        user = authenticate(request, username=username, password=password)
        # checking if the user is not None and is an owner
        if user is not None and user.is_director == True:
            form = login(request, user)
            return redirect('/owner_dashboard')
                
        # checking if the user is not None and is a manager
        if user is not None and user.is_manager == True:
            form = login(request, user)
            return redirect('/manager_dashboard')
        
        if user is not None and user.is_salesagent == True:
            form = login(request, user)
            return redirect('/home')
            
        else:
            print('something went wrong')
    form = AuthenticationForm
    return render(request, 'happy_hoeapp/login.html', {'form': form, 'title': 'Login'})

#view for the owner dashboard
def owner(request):
    
    # Get totals for dashboard cards

    total_sales = Sale.objects.count()
    total_stock = Stock.objects.aggregate(total=Sum('total_quantity'))['total'] 
    total_credit_sales = CreditSale.objects.count()
    total_users = Userprofile.objects.count()
    
    # Get low stock alerts (items with quantity less than 10)
    low_stock_items = Stock.objects.filter(total_quantity__lt=10)
    
    # Get stock data for bar graph - aggregate by product name
    stock_data = []
    for choice in Stock.product_choices:
        product_name = choice[0]  # Get the value from the choice tuple
        quantity = Stock.objects.filter(product_name=product_name).aggregate(
            total=Coalesce(Sum('total_quantity'), 0)
        )['total']
        stock_data.append({
            'product_name': product_name,
            'quantity': quantity
        })
    
    # Get sales data for pie chart - aggregate total sales value by product
    sales_data = []
    for choice in Stock.product_choices:
        product_name = choice[0]
        total_sales_value = Sale.objects.filter(product_name__product_name=product_name).aggregate(
            total=Coalesce(Sum(F('quantity') * F('unit_price'), output_field=FloatField()), 0.0)
        )['total']
        sales_data.append({
            'product_name': product_name,
            'total_sales': float(total_sales_value)
        })
    
    # Get all products for the table

    stocks = Stock.objects.all().order_by('-id')
    
    context = {
        'total_sales': total_sales,
        'total_stock': total_stock,
        'total_credit_sales': total_credit_sales,
        'total_users': total_users,
        'low_stock_items': low_stock_items,
        'stock_data_json': json.dumps(stock_data, cls=DjangoJSONEncoder),
        'sales_data_json': json.dumps(sales_data, cls=DjangoJSONEncoder),
        'stocks': stocks,

        
    }

    

    return render(request, 'happy_hoeapp/owner_dashboard.html', context, )

#view for the managers dashboard
def manager(request):

    return render(request, 'happy_hoeapp/manager_dashboard.html')

def  signup(request):
    if request.method == 'POST':
        form = UserCreation(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')

            email = form.cleaned_data.get('email')
            return redirect('/')
    else: 
        form = UserCreation()
    return render(request, 'happy_hoeapp/signup.html', {'form': form})

def user_detail (request, user_id):
    user = get_object_or_404(Userprofile,id=user_id)
    return render(request, 'happy_hoeapp/user_detail.html', {'user': user})

def edit_user(request, pk):
    user=Userprofile.objects.get(id=pk)
    form = UserCreation(instance=user)

    if request.method=='POST':
        form = UserCreation(request.POST, instance=user)
        if form.is_valid():
            updated_user= form.save(commit=False)
            updated_user.save()
            return redirect('all_users')
    context = {
        'form': form,
        'user': user,
        'title': 'Edit User'
    }
    return render(request, 'happy_hoeapp/edit_user.html', context)

def delete_user(request, user_id):
    user = get_object_or_404(Userprofile, id=user_id)

    if request.method == 'POST':
        user.delete()
        return redirect('user')  # Redirect to user list or homepage

    return render(request, 'users/confirm_delete.html', {'user': user})

def edit_stock(request, pk):
    stock_item = Stock.objects.get(id=pk)
    form = EditStockForm(instance=stock_item)

    if request.method == 'POST':
        form = EditStockForm(request.POST, instance=stock_item)
        if form.is_valid():
            updated_stock = form.save(commit=False)
            updated_stock.total_quantity = stock_item.total_quantity + updated_stock.received_quantity
            updated_stock.save()
            return redirect('index')  # or wherever you want

    return render(request, 'happy_hoeapp/edit.html', {'form': form, 'stock': stock_item})



def edit_sale(request, pk):
    sale_item = Sale.objects.get(id=pk)
    form = UpdateSaleForm(request.POST or None, instance=sale_item) # use request.POST or None to handle both GET and POST requests
    if request.method == 'POST':
        if form.is_valid():
            
            
            form.save()
    
            # to add to the remaining stock quantity is increasing
            
            return redirect('sales')
    
    return render(request,"happy_hoeapp/edit_sale.html", {"form": form})

def sale_detail(request,pk):
    sale= Sale.objects.get(id=pk)
    return render(request, 'happy_hoeapp/sale_detail.html', {'sale': sale})

def create_credit_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)

    if request.method == 'POST':
        form = CreditSaleForm(request.POST)
        if form.is_valid():
            credit_sale = form.save(commit=False)
            credit_sale.sale = sale
            credit_sale.save()
            return redirect('sales')  # or some detail view
    else:
        form = CreditSaleForm()

    return render(request, 'sales/create_credit_sale.html', {'form': form, 'sale': sale})


# Edit existing CreditSale
def edit_credit_sale(request, pk):
    credit_sale = get_object_or_404(CreditSale, pk=pk)

    if request.method == 'POST':
        form = CreditSaleForm(request.POST, instance=credit_sale)
        if form.is_valid():
            form.save()
            return redirect('sales')
    else:
        form = CreditSaleForm(instance=credit_sale)

    return render(request, 'sales/edit_credit_sale.html', {'form': form, 'credit_sale': credit_sale})

def sales(request):
    # getting all the registered sales from our data base
    sales=Sale.objects.all().order_by('-id')
    return render(request,"happy_hoeapp/transactions.html", {"sales": sales})

def delete_stock(request, pk):
    delete_stock = get_object_or_404(Stock,id=pk)

    if request.method == 'POST':
        data=request.POST
        delete_stock.delete()
        messages.success(request, "stock deleted successfully.")
        return redirect('index')

    context = {
        'delete_stock': delete_stock,
    }
    return render(request, 'happy_hoeapp/delete_product.html', context)


def delete_sale(request, pk):
    sale = get_object_or_404(Sale, id=pk)
    
    if request.method == 'POST':
        # Restore the stock quantity before deleting the sale
        product = sale.product_name
        product.total_quantity += sale.quantity
        product.save()
        
        # Delete the sale
        sale.delete()
        return redirect('sales')
        
    return render(request, 'happy_hoeapp/delete_sale.html', {'sale': sale})

def add_fullstock(request):
    
        
    return render(request, "add.html")

def Logout(request):
    return render(request, 'happy_hoeapp/logout.html')
    

def base3 (request):
    return render(request, 'happy_hoeapp/base3.html')
