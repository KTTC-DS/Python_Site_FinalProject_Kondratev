from django.contrib import admin
from .models import RentalRequest, Transaction


@admin.register(RentalRequest)
class RentalRequestAdmin(admin.ModelAdmin):
    list_display = ('ad', 'renter', 'start_date', 'end_date', 'status', 'created_at')
    list_filter = ('status', 'start_date')
    search_fields = ('ad__title', 'renter__username')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('rental_request', 'amount', 'payment_date', 'is_paid')
    list_filter = ('is_paid', 'payment_date')