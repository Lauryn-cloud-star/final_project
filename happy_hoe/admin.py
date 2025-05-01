from django.contrib import admin

# accessing our own models
from .models import *
# Register your models here.

admin.site.register(Stock)
admin.site.register(Sale)
admin.site.register(Category)
admin.site.register(CreditSale)
admin.site.register(Userprofile)
