from django.contrib import admin
from django.db import models
from .models import Category, Expense


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'budget', 'get_total_spent', 'get_remaining_budget']
    search_fields = ['name']
    ordering = ['name']
    
    def get_total_spent(self, obj):
        total = obj.expenses.aggregate(total=models.Sum('amount'))['total'] or 0
        return f"${total:.2f}"
    get_total_spent.short_description = 'Total Gastado'
    
    def get_remaining_budget(self, obj):
        total_spent = obj.expenses.aggregate(total=models.Sum('amount'))['total'] or 0
        remaining = obj.budget - total_spent
        return f"${remaining:.2f}"
    get_remaining_budget.short_description = 'Presupuesto Restante'


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'category', 'date', 'formatted_amount']
    list_filter = ['category', 'date']
    search_fields = ['name', 'category__name']
    date_hierarchy = 'date'
    ordering = ['-date']
    
    def formatted_amount(self, obj):
        return f"${obj.amount:.2f}"
    formatted_amount.short_description = 'Monto'
