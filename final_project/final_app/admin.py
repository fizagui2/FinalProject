from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Category, Comment, Post, User, Vote, Product, Cart, CartItem, Order, OrderItem, Listing, ListingInterest


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

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'body', 'author__username')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('body', 'author__username', 'post__title')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'value')
    list_filter = ('value',)


class ListingInterestInline(admin.TabularInline):
    model = ListingInterest
    extra = 0
    readonly_fields = ('buyer', 'created_at')
    can_delete = False


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'price', 'interest_count', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description', 'seller__username')
    inlines = [ListingInterestInline]

    @admin.display(description='Interested buyers')
    def interest_count(self, obj):
        return obj.interests.count()


@admin.register(ListingInterest)
class ListingInterestAdmin(admin.ModelAdmin):
    list_display = ('listing', 'buyer', 'created_at')
    search_fields = ('listing__title', 'buyer__username')
