from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
# accessing our models inorder to create corresponding forms

from .models import *
class AddStockForm (ModelForm):
    class Meta:
        model = Stock
        fields = "__all__"    

class AddSaleForm (ModelForm):
    is_credit_sale = forms.BooleanField(required=False, label="Credit Sale")
    customer_name = forms.CharField(required=False, label="Customer Name")
    national_id = forms.CharField(required=False, label="National ID")
    customer_contact = forms.CharField(required=False, label="Contact")
    amount_received = forms.IntegerField(required=True, label="Amount Received")
    class Meta:
        model = Sale
        # fields = ["product_name", "quantity", "cost_of_stock", "unit_cost", "unit_cost", "unit_price", "date_of_stock"]
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(AddSaleForm, self).__init__(*args, **kwargs)
        self.fields['quantity'].widget.attrs.update({'class': 'form-control'})





class UpdateStockForm(ModelForm):
    class Meta:
        model = Stock
        fields = ["received_quantity"]

class UserCreation(UserCreationForm):
    class Meta:
        model = Userprofile
        fields = '__all__'
        
    def save(self, commit = True):
        user = super(UserCreation,self).save(commit = False)
        if commit:
            user.is_active = True
            user.is_staff = True
            user.save()
        return user
            
from django import forms


class EditStockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = '__all__'  # adjust based on your model

class UpdateSaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = '__all__'  # adjust as per your model

class CreditSaleForm(forms.ModelForm):
    class Meta:
        model = CreditSale
        fields = [
            'sale',
            'customer_name',
            'national_id',
            'contact',
            'location',
            'due_date',
            'amount_paid',
            'balance',
            'status',
            
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = "__all__"
        widgets = {
            'opening_date': forms.DateInput(attrs={'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+256XXXXXXXXX'})
        }