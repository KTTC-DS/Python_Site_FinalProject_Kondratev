from django.contrib import admin
from .models import Ad, Category


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price_per_day', 'location', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'location')
    search_fields = ('title', 'description')
    actions = ['approve_ads']

    def approve_ads(self, request, queryset):
        queryset.update(is_approved=True)
    approve_ads.short_description = "Одобрить выбранные объявления"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')