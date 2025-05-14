from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
# accessing our models inorder to create corresponding forms

from .models import *
class Produce(ModelForm):
    class Meta:
        model = Produce
        fields = '__all__'
        
class AddStockForm (ModelForm):
    class Meta:
        model = Stock
        fields = "__all__"    

class AddSaleForm (ModelForm):
    product_name = forms.ModelChoiceField(
        queryset=Stock.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'product-select'})
    )
    quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'quantity-input'})
    )

    
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
    
class UpdateUserCreation(forms.ModelForm):
    class  Meta:
        model = Userprofile
        fields='__all__'
    
class EditStockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = '__all__'  

class UpdateSaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = '__all__'  

class CreditSaleForm(forms.ModelForm):
    class Meta:
        model = CreditSale
        fields ='__all__'
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'})
        }



class UpdateCreditSaleForm(forms.ModelForm):
    class Meta:
        model = CreditSale
        fields = ['status']
        

    def clean_amount_paid(self):
        amount_paid = self.cleaned_data.get('amount_paid')
        current_amount = self.instance.amount_paid
        if amount_paid < current_amount:
            raise forms.ValidationError("New payment amount cannot be less than previous amount")
        return amount_paid

    def save(self, commit=True):
        credit_sale = super().save(commit=False)
        credit_sale.balance = credit_sale.sale.total_sale() - credit_sale.amount_paid
        if credit_sale.balance <= 0:
            credit_sale.status = 'PAID'
        elif credit_sale.due_date < timezone.now().date():
            credit_sale.status = 'OVERDUE'
        if commit:
            credit_sale.save()
        return credit_sale




class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = "__all__"
        widgets = {
            'opening_date': forms.DateInput(attrs={'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+256XXXXXXXXX'})
        }