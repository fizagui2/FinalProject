from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (Category, User, Product, Cart, CartItem, Order, OrderItem, )
from .models import Category, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'display_name', 'is_staff')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('GameHub profile', {'fields': ('display_name', 'bio')}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','product_type','category','price','stock','created_at',)
    list_filter = ('product_type','category',)
    search_fields = ('name','description',)
    prepopulated_fields = {'slug':('name',)}

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','user','status','total','created_at',)
    list_filter = ('status',)

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
