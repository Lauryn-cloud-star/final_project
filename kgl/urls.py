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
    path('logout/', views.Logout, name='logout'),
    path('home/', views.index, name='index'),
    path('add_stock/<str:pk>/', views.add_stock, name="add_stock"),
    path('procurement/', views.Procurement, name="procurement"),
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
    # path('credit_sale/create/<int:sale_id>/', views.create_credit_sale, name='create_credit_sale'),
    # path('credit_sale/edit/<int:pk>/', views.edit_credit_sale, name='edit_credit_sale'),
    # path('credit-sale/<int:pk>/', views.credit_sale_detail, name='credit_sale_detail'),
    path('delete_stock/<str:pk>/',views.delete_stock, name="delete_stock"),
    path('sale/<int:pk>/delete/', views.delete_sale, name='delete_sale'),
    path('categories/', views.categories, name='categories'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('categories/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('base3/', views.base3, name='base3'),
    path('users/', views.all_users, name='users'),
     path('users/<int:user_id>/', views.user_detail, name='user_detail'),
     path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('branch/add/', views.add_branch, name='add_branch'),
    path('users/<int:pk>/edit/', views.edit_user, name='edit_user'),
    path('branch/', views.all_branches, name='branches'),
    path('credit_sales/', views.all_credit_sales, name='credit_sales'),
    path('create_credit_sale/<int:sale_id>/', views.create_credit_sale, name='create_credit_sale'),
    path('update_credit_sale/<int:pk>/', views.update_credit_sale, name='update_credit_sale'),
    path('credit_sale_detail/<int:pk>/', views.credit_sale_detail, name='credit_sale_detail'),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('search/', views.search, name='search'),

    path('branches/', views.branch_list, name='branch_list'),
    path('branch/<int:branch_id>/manager/', views.manager, name='manager'),
]
    

