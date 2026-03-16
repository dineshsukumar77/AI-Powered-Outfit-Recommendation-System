from django.contrib import admin
from .models import UserAccount, Person, Wardrobe, WardrobeItem


@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ['username', 'created_at']
    search_fields = ['username']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


class WardrobeItemInline(admin.TabularInline):
    model = WardrobeItem
    extra = 0


@admin.register(Wardrobe)
class WardrobeAdmin(admin.ModelAdmin):
    inlines = [WardrobeItemInline]
    list_display = ['name', 'created_at']


@admin.register(WardrobeItem)
class WardrobeItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'wardrobe', 'category', 'color']
    list_filter = ['category', 'wardrobe']
