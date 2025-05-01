from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404

# Create your views here.
from .models import *
from django.urls import reverse
from .forms import *
# borrowing decorators for authentication
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserCreation

# view for the index page
def index(request):
    context = {
        "site_name": "happy hoe management system",       
        "products": ["G'nuts", "Beans", "Maize", "soybeans", "cowpeas"],
    }
    # getting all the registered stock from our data base
    stocks=Stock.objects.all().order_by('-id')

    return render(request,"happy_hoeapp/index.html", {"stocks": stocks})

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
def all_stock(request):
    return render(request,"happy_hoeapp/allstock.html")

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
def receipt(request):
    # getting all the registered sales from our data base
    sales=Sale.objects.all().order_by('-id')
    return render(request,"happy_hoeapp/receipt.html", {"sales": sales})
def sales(request):
    # getting all the registered sales from our data base
    sales=Sale.objects.all().order_by('-id')
    return render(request,"happy_hoeapp/transactions.html", {"sales": sales})

# aview to handle a link to handle a particular item for a sale
def stock_detail(request, stock_id):
    stock = Stock.objects.get(id=stock_id)

    return render(request, 'happy_hoeapp/detail.html', {'stock': stock})
def issue_item(request, pk):
    issued_item = Stock.objects.get(id=pk)

    if request.method == 'POST':
        sales_form = AddSaleForm(request.POST)
        if sales_form.is_valid():
            new_sale = sales_form.save(commit=False)
            new_sale.product_name = issued_item
            new_sale.payment_method = sales_form.cleaned_data['payment_method']
            new_sale.unit_price = issued_item.unit_price
            new_sale.sales_agent = request.user  # if you're tracking sales agent
            new_sale.amount_receiced = sales_form.cleaned_data['amount_received']
            # Optional: auto-fill some fields
            if not new_sale.customer_name:
                new_sale.customer_name = "Anonymous"
            if not new_sale.payment_method:
                new_sale.payment_method = "Cash"
            

            issued_quantity = new_sale.quantity
            if issued_quantity > issued_item.total_quantity:
                sales_form.add_error('quantity', 'Not enough stock available.')
            else:
                new_sale.save()
                issued_item.total_quantity -= issued_quantity
                issued_item.save()
                return redirect('receipt')
    else:
        sales_form = AddSaleForm()

    return render(request, 'happy_hoeapp/issue_item.html', {
        'sales_form': sales_form,
        'issued_item': issued_item
    })


#  view for the login page
def Login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password =request.POST.get('password')
        # ckecking the logging in user
        user = authenticate(request, username=username, password=password)
        # checking if the user is not None and is an owner
        if user is not None and user.is_owner == True:
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
    return render(request, 'happy_hoeapp/owner_dashboard.html')
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
            return redirect('/login')
    else: 
        form = UserCreation()
    return render(request, 'happy_hoeapp/signup.html', {'form': form})


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

def receipt_detail(request, receipt_id):
    receipt = Sale.objects.get(id=receipt_id)
    return render(request, 'happy_hoeapp/final_receipt.html', {'receipt': receipt})