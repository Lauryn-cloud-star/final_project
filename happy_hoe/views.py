from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from django.db.models import Q, Subquery, OuterRef
# Create your views here.
from .models import *
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import *
# borrowing decorators for authentication
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserCreation

from django.db.models import Sum, F, FloatField,Count
from django.db.models.functions import Coalesce
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.humanize.templatetags.humanize import intcomma
 
def can_view_branch(user, branch):
    """Check if user can view data from a specific branch"""
    return user.is_director or user.branch == branch

@login_required
def all_branches(request):
    branches = Branch.objects.all()
    return render(request, 'happy_hoeapp/branch.html', {'branches': branches})


@login_required
@user_passes_test(lambda u: u.is_director)
def branch_list(request):
    branches = Branch.objects.all().annotate(
        total_stock=Coalesce(Sum('branch_stock__total_quantity'), 0),
        staff_count=Count('userprofile'),
        manager=Subquery(
            Userprofile.objects.filter(
                branch=OuterRef('pk'),
                is_manager=True
            ).values('id')[:1]
        )
    )

    for branch in branches:
        branch.manager = Userprofile.objects.filter(
            branch=branch,
            is_manager=True
        ).first()

    context = {
        'branches': branches,
        'title': 'Branch Overview'
    }
    
    return render(request, 'happy_hoeapp/branch_detail.html', context)


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
    if request.user.is_director:
        users = Userprofile.objects.exclude(is_superuser=True).order_by('-date_joined')
    else:
        users = Userprofile.objects.filter(branch=request.user.branch)


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

# stock_details
@login_required
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
    if request.user.is_director:
        stocks = Stock.objects.all()
    else:
        stocks = Stock.objects.filter(branch=request.user.branch)
    
    context = {
        'stocks': stocks,
        'title': 'Stock List'
    }

    return render(request,"happy_hoeapp/index.html", {"stocks": stocks})

@login_required
# A view for creating the categories
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


@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
def add_sale(request):
    return render(request,"happy_hoeapp/add_sale.html")
#  view for the addstock
def creditsale(request):
    return render(request,"happy_hoeapp/creditsale.html")


#  view for the all_sales
def all_sales(request):
    return render(request,"happy_hoeapp/all_sales.html")

#  view for the receipt
@login_required
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


# aview for sellingout an item
@login_required
@user_passes_test(lambda u: u.is_salesagent or u.is_manager)
def issue_item(request,pk):
    stock_item = Stock.objects.get(id=pk)
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
        'issued_item': issued_item,
        'stock': stock_item
    })

@login_required
def receipt_detail(request, receipt_id):
    receipt = Sale.objects.get(id=receipt_id)
    return render(request, 'happy_hoeapp/final_receipt.html', {'receipt': receipt})

@login_required
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
@login_required
def owner(request):
    # getting all the queries from tha database
    sales = Sale.objects.all()
    stock = Stock.objects.all()
    branches = Branch.objects.all()
    users = Userprofile.objects.all()
    credit_sales = Sale.objects.filter(payment_method='Credit')

    # calculating tha total amounts
    total_sales_amount = Sale.objects.aggregate(
    total=Sum(F('unit_price') * F('quantity'))
)['total']
   
    total_credit_saless = CreditSale.objects.aggregate(
            total=Sum(F('sale__unit_price') * F('sale__quantity'))
        )['total']


    stock_data = list(stock.values('product_name').annotate(
        quantity=Sum('total_quantity')
    ))
    
    sales_data = list(Sale.objects.values('product_name__product_name').annotate(
        total_amount=Sum(F('unit_price') * F('quantity')),
        product_name=F('product_name__product_name')
    ).order_by('-total_amount'))
    

    

    context = {
        'total_saless': f"UGX {intcomma(total_sales_amount)}",
        'total_sales': sales.count(),
        'total_stock': stock.aggregate(Sum('total_quantity'))['total_quantity__sum'] or 0,
        'total_credit_sales': credit_sales.count(),
        'total_credit_saless': f"UGX {intcomma(total_credit_saless)}",
        'total_users': users.count(),
        'stock_data_json': json.dumps(stock_data, cls=DjangoJSONEncoder),
        'sales_data_json': json.dumps(sales_data, cls=DjangoJSONEncoder),
        'stocks': stock,
        'title': 'Director Dashboard'

    }
   
    
    return render(request, 'happy_hoeapp/owner_dashboard.html', context)

#view for the managers dashboard
@login_required
def manager(request):
 # Get manager's branch
    branch = request.user.branch
    
    # Filter queryset by branch
    stock = Stock.objects.filter(branch=branch)
    sales = Sale.objects.filter(branch=branch)
    credit_sales = CreditSale.objects.filter(sale__branch=branch)
    users = Userprofile.objects.filter(branch=branch)

    # Calculate totals
    total_sales_amount = sales.aggregate(
        total=Coalesce(Sum(F('unit_price') * F('quantity')), 0, output_field=FloatField())
    )['total']

    total_credit_amount = credit_sales.aggregate(
        total=Coalesce(Sum(F('amount_paid')), 0, output_field=FloatField())
    )['total']

    context = {
        'branch_name': branch.branch_name,
        'total_sales': f"UGX {intcomma(total_sales_amount)}",
        'total_transactions': sales.count(),
        'total_stock': stock.aggregate(Sum('total_quantity'))['total_quantity__sum'] or 0,
        'total_credit_sales': credit_sales.count(),
        'total_credit_amount': f"UGX {intcomma(total_credit_amount)}",
        'total_users': users.count(),
        'stock_data_json': json.dumps(list(stock.values('product_name').annotate(
            quantity=Sum('total_quantity')
        ).order_by('-quantity')), cls=DjangoJSONEncoder),
        'sales_data_json': json.dumps(list(sales.values('product_name').annotate(
            total=Sum(F('unit_price') * F('quantity'))
        ).order_by('-total')), cls=DjangoJSONEncoder),
        'stocks': stock,
        'title': f'{branch.branch_name} Dashboard'
    }
    
    return render(request, 'happy_hoeapp/manager_dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_director or u.is_manager)
def signup(request):
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


# view for seeing the details of a particular user
@login_required
def user_detail (request, user_id):
    user = get_object_or_404(Userprofile,id=user_id)
    return render(request, 'happy_hoeapp/user_detail.html', {'user': user})


# view for editting the user
@login_required
@user_passes_test(lambda u: u.is_director or u.is_manager)
def edit_user(request, pk):
    user = get_object_or_404(Userprofile, id=pk)
    if request.method == 'POST':
        form = UpdateUserCreation(request.POST, instance=user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'User {user.username} updated successfully!')
                return redirect('users')
            except IntegrityError as e:
                messages.error(request, 'Error updating user. This username or email may already be in use.')
    else:
        form = UpdateUserCreation(instance=user)
    
    return render(request, 'happy_hoeapp/edit_user.html', {'form': form,'title': 'edit User'})

#view for deleting the particular user
@login_required
@user_passes_test(lambda u: u.is_director or u.is_manager)
def delete_user(request, user_id):
    user = get_object_or_404(Userprofile, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" has been deleted successfully.')
        return redirect('users')
    
    return redirect('users')
# a view for adding stock
@login_required
def add_fullstock(request):
    
        
    return render(request, "add.html")


# a view for deleting a particular stock item
@login_required
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


# view for editing a particular stock item
@login_required
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

# a view for the sales table
@login_required
def sales(request):
    # getting all the registered sales from our data base
    sales=Sale.objects.all().order_by('-id')
    return render(request,"happy_hoeapp/transactions.html", {"sales": sales})


# view for editting a particular sale item
@login_required
def edit_sale(request, pk):
   
    sale_item = Sale.objects.get(id=pk)
    form = UpdateSaleForm(request.POST or None, instance=sale_item) # use request.POST or None to handle both GET and POST requests
    if request.method == 'POST':
        if form.is_valid():
            
            
            form.save()
            
            return redirect('sales')
    
    return render(request,"happy_hoeapp/edit_sale.html", {"form": form})

# view for seeing a particular sale details
@login_required
def sale_detail(request,pk):
    sale= Sale.objects.get(id=pk)
    return render(request, 'happy_hoeapp/sale_detail.html', {'sale': sale})


# view foe seeing all the credit sales
@login_required
def all_credit_sales(request):
    credit_sales = CreditSale.objects.all().order_by('-due_date')
    
    context = {
        'credit_sales': credit_sales,
        'title': 'Credit Sales'
    }
    return render(request, 'happy_hoeapp/credit_sales.html', context)

# view for adding a credit sale
@login_required
def create_credit_sale(request, sale_id):
    # Get the existing sale
    sale = get_object_or_404(Sale, id=sale_id)
    
    # Check if this sale is already a credit sale
    if hasattr(sale, 'credit_details'):
        messages.warning(request, 'This sale already has a credit record!')
        return redirect('credit_sales')
    
    # Update the sale payment method to 'Credit'
    sale.payment_method = 'Credit'
    sale.payment_status = 'PENDING'
    sale.save()
    
    if request.method == 'POST':
        form = CreditSaleForm(request.POST)
        if form.is_valid():
            credit_sale = form.save(commit=False)
            credit_sale.sale = sale
            
            # Calculate balance
            credit_sale.balance = sale.total_sale() - credit_sale.amount_paid
            
            # Set status based on balance
            if credit_sale.balance <= 0:
                credit_sale.status = 'PAID'
            elif credit_sale.due_date < timezone.now().date():
                credit_sale.status = 'OVERDUE'
            else:
                credit_sale.status = 'PENDING'
                
            credit_sale.save()
            
            messages.success(request, 'Credit sale added successfully!')
            return redirect('credit_sales')
    else:
        # Pre-fill the form with customer info if available
        initial_data = {}
        if sale.customer_name:
            initial_data['customer_name'] = sale.customer_name
        
        form = CreditSaleForm(initial=initial_data)
    
    context = {
        'form': form,
        'sale': sale
    }
    
    return render(request, 'happy_hoeapp/create_credit_sale.html', context)# Edit existing CreditSale

# view for editing the credit sale
@login_required
def update_credit_sale(request, pk):
    credit_sale = get_object_or_404(CreditSale, pk=pk)
    
    if request.method == 'POST':
        form = UpdateCreditSaleForm(request.POST, instance=credit_sale)
        if form.is_valid():
            form.save()
            messages.success(request, f'Credit sale for {credit_sale.customer_name} updated successfully!')
            return redirect('credit_sales')
    else:
        form = UpdateCreditSaleForm(instance=credit_sale)
    
    context = {
        'form': form,
        'credit_sale': credit_sale
    }
    
    return render(request, 'happy_hoeapp/edit_credit_sale.html', context)

@login_required
def credit_sale_detail(request, pk):
    credit_sale = get_object_or_404(CreditSale, pk=pk)
    return render(request, 'happy_hoeapp/credit_sale_detail.html', {
        'credit_sale': credit_sale
    })


# a view for deleting a aparticular sale
@login_required
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




# view for logout
@login_required
def Logout(request):
    return render(request, 'happy_hoeapp/logout.html')
    

def base3 (request):
    return render(request, 'happy_hoeapp/base3.html')

@login_required
def user_profile(request, user_id):
    # Ensure users can only view their own profile unless they're director/manager
    if request.user.id != user_id and not (request.user.is_director or request.user.is_manager):
        messages.error(request, "You can only view your own profile")
        return redirect('home')
        
    user = get_object_or_404(Userprofile, id=user_id)
    context = {
        'profile': user,
        'title': f'Profile - {user.get_full_name() or user.username}'
    }
    return render(request, 'happy_hoeapp/profile.html', context)




@login_required
def search_stock(request):
    query = request.GET.get('q', '')
    if query:
        stocks = Stock.objects.filter(
            Q(product_name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(branch__branch_name__icontains=query)
        )
    else:
        stocks = Stock.objects.all()
    
    if not request.user.is_director and not request.user.is_manager:
        stocks = stocks.filter(branch=request.user.branch)
        context = {
        'stocks': stocks,
        'query': query,
        'title': 'Search '
    }
    return render(request, 'happy_hoeapp/stock_list.html', context)

@login_required
def search_sales(request):
    query = request.GET.get('q', '')
    if query:
        sales = Sale.objects.filter(
            Q(product_name__icontains=query) |
            Q(customer_name__icontains=query) |
            Q(payment_method__icontains=query) |
            Q(branch__branch_name__icontains=query) |
            Q(date__icontains=query)
        )                                  
    else:
        sales = Sale.objects.all()
    
    if not request.user.is_director and not request.user.is_manager:
        sales = sales.filter(branch=request.user.branch)
        
    context = {
        'sales': sales,
        'query': query,
        'title': 'Search Sales'
    }
    return render(request, 'happy_hoeapp/sales_list.html', context)

@login_required
def search(request):
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'stock')
    
    if search_type == 'stock':
        items = Stock.objects.filter(
            Q(product_name__icontains=query) |
            Q(Category_name__category_name__icontains=query) |  # Changed from category to Category_name
            Q(branch__branch_name__icontains=query)
        ) if query else Stock.objects.all()
        template = 'happy_hoeapp/stock_list.html'
    else:
        items = Sale.objects.filter(
            Q(product_name__icontains=query) |
            Q(customer_name__icontains=query) |
            Q(payment_method__icontains=query) |
            Q(branch__branch_name__icontains=query)
        ) if query else Sale.objects.all()
        template = 'happy_hoeapp/sales_list.html'
    
    if not request.user.is_director and not request.user.is_manager:
        items = items.filter(branch=request.user.branch)
    
    context = {
        'query': query,
        'items': items,
        'search_type': search_type,
        'title': f'Search {search_type.title()}'
    }
    return render(request, template, context)