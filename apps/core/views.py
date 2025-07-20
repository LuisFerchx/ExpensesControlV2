from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from .models import Expense, Category
from .forms import ExpenseForm, CategoryForm


class ExpenseListView(LoginRequiredMixin, ListView):
    """Vista para listar todos los gastos"""
    model = Expense
    template_name = 'core/expense_list.html'
    context_object_name = 'expenses'
    ordering = ['-date']
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['total_expenses'] = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
        context['category_totals'] = Category.objects.annotate(
            total_spent=Sum('expenses__amount')
        ).values('name', 'budget', 'total_spent')
        return context


class ExpenseDetailView(LoginRequiredMixin, DetailView):
    """Vista para mostrar detalles del gasto"""
    model = Expense
    template_name = 'core/expense_detail.html'
    context_object_name = 'expense'


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear nuevos gastos"""
    model = Expense
    form_class = ExpenseForm
    template_name = 'core/expense_form.html'
    success_url = reverse_lazy('core:expense_list')
    
    def form_valid(self, form):
        messages.success(self.request, '¡Gasto creado exitosamente!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrija los errores a continuación.')
        return super().form_invalid(form)


class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar gastos existentes"""
    model = Expense
    form_class = ExpenseForm
    template_name = 'core/expense_form.html'
    success_url = reverse_lazy('core:expense_list')
    
    def form_valid(self, form):
        messages.success(self.request, '¡Gasto actualizado exitosamente!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrija los errores a continuación.')
        return super().form_invalid(form)


class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar gastos"""
    model = Expense
    template_name = 'core/expense_confirm_delete.html'
    success_url = reverse_lazy('core:expense_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '¡Gasto eliminado exitosamente!')
        return super().delete(request, *args, **kwargs)


# Vistas de Categorías
class CategoryListView(LoginRequiredMixin, ListView):
    """Vista para listar todas las categorías"""
    model = Category
    template_name = 'core/category_list.html'
    context_object_name = 'categories'
    ordering = ['name']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get categories with total spent
        categories_with_totals = Category.objects.annotate(
            total_spent=Sum('expenses__amount')
        )
        context['categories'] = categories_with_totals
        
        # Calculate summary statistics
        total_budget = sum(cat.budget for cat in categories_with_totals)
        total_spent = sum(cat.total_spent or 0 for cat in categories_with_totals)
        total_remaining = total_budget - total_spent
        
        context['total_budget'] = total_budget
        context['total_spent'] = total_spent
        context['total_remaining'] = total_remaining
        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear nuevas categorías"""
    model = Category
    form_class = CategoryForm
    template_name = 'core/category_form.html'
    success_url = reverse_lazy('core:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, '¡Categoría creada exitosamente!')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar categorías existentes"""
    model = Category
    form_class = CategoryForm
    template_name = 'core/category_form.html'
    success_url = reverse_lazy('core:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, '¡Categoría actualizada exitosamente!')
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar categorías"""
    model = Category
    template_name = 'core/category_confirm_delete.html'
    success_url = reverse_lazy('core:category_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '¡Categoría eliminada exitosamente!')
        return super().delete(request, *args, **kwargs)


# Vista del Dashboard
def dashboard(request):
    """Vista del dashboard con resumen de gastos"""
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_budget = Category.objects.aggregate(total=Sum('budget'))['total'] or 0
    remaining_budget = total_budget - total_expenses
    
    category_summary = Category.objects.annotate(
        total_spent=Sum('expenses__amount')
    ).values('name', 'budget', 'total_spent')
    
    recent_expenses = Expense.objects.select_related('category').order_by('-date')[:5]
    
    context = {
        'total_expenses': total_expenses,
        'total_budget': total_budget,
        'remaining_budget': remaining_budget,
        'category_summary': category_summary,
        'recent_expenses': recent_expenses,
    }
    
    return render(request, 'core/dashboard.html', context)
