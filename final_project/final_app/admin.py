from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Category, Comment, Post, User, Vote


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
