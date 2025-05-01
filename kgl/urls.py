"""
URL configuration for kgl project.

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
from django.urls import path
from happy_hoe import views

# django login view for authentication
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # view for the index page
    path('', views.Login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='happy_hoeapp/logout.html'), name="logout"),
    path('home', views.index, name='index'),
    path('add_stock/<str:pk>/', views.add_stock, name="add_stock"),
    path('all_stock/', views.all_stock, name="all_stock"),
    path('add_sale', views.add_sale, name="add_sale"),
    path('all_sales/', views.all_sales, name="all_sales"),
    path('receipt/', views.receipt, name="receipt"),
     path('home/<int:stock_id>/', views.stock_detail, name="stock_detail"),
    path('creditsale', views.creditsale, name="creditsale"),
    # setting a url for a particular sell item
    path('issue_item/<str:pk>/', views.issue_item, name="issue_item"), 
    path('receipt/<int:receipt_id>/', views.receipt_detail, name="receipt_detail"),
    path('signup/', views.signup, name="signup"),
    path('salesagent_dashboard/', views.index, name="salesagent_dashboard"),
    path('manager_dashboard/', views.manager, name="manager_dashboard"),
    path('owner_dashboard/', views.owner, name="owner_dashboard"),
    path('sales/', views.sales, name="sales"),
    path('edit_stock/<str:pk>/', views.edit_stock, name="edit_stock"),
    # path('edit_sale/<str:pk>/', views.edit_sale, name="edit_sale"),
    path('sales/<int:pk>/', views.sale_detail, name="sale_detail"),
    path('sales/<int:pk>edit/', views.edit_sale, name="edit_sale"),
    path('credit-sale/create/<int:sale_id>/', views.create_credit_sale, name='create_credit_sale'),
    path('credit-sale/edit/<int:pk>/', views.edit_credit_sale, name='edit_credit_sale'),
    # path('credit-sale/<int:pk>/', views.credit_sale_detail, name='credit_sale_detail'),

    
]
