from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, date
from .models import Expense, Category
from .forms import ExpenseForm, CategoryForm


class ExpenseListView(LoginRequiredMixin, ListView):
    """Vista para listar todos los gastos"""
    model = Expense
    template_name = 'core/expense_list.html'
    context_object_name = 'expenses'
    ordering = ['-date']
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Expense.objects.filter(category__user=self.request.user)
        
        # Filtrar por mes si se proporciona
        month_param = self.request.GET.get('month')
        if month_param:
            try:
                month_date = datetime.strptime(month_param, '%Y-%m').date()
                # Filtrar gastos del mes seleccionado
                queryset = queryset.filter(date__year=month_date.year, date__month=month_date.month)
            except ValueError:
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el mes seleccionado
        month_param = self.request.GET.get('month')
        selected_month = None
        if month_param:
            try:
                selected_month = datetime.strptime(month_param, '%Y-%m').date()
            except ValueError:
                pass
        
        # Filtrar categorías por mes si se selecciona
        categories_queryset = Category.objects.filter(user=self.request.user)
        if selected_month:
            categories_queryset = categories_queryset.filter(month__year=selected_month.year, month__month=selected_month.month)
        
        context['categories'] = categories_queryset
        
        # Calcular totales filtrados por mes
        expenses_queryset = Expense.objects.filter(category__user=self.request.user)
        if selected_month:
            expenses_queryset = expenses_queryset.filter(date__year=selected_month.year, date__month=selected_month.month)
        
        context['total_expenses'] = expenses_queryset.aggregate(total=Sum('amount'))['total'] or 0
        
        # Calcular totales por categoría filtrados por mes
        category_totals = Category.objects.filter(user=self.request.user)
        if selected_month:
            category_totals = category_totals.filter(month__year=selected_month.year, month__month=selected_month.month)
        
        category_totals = category_totals.annotate(
            total_spent=Sum('expenses__amount')
        ).values('name', 'budget', 'total_spent')
        
        context['category_totals'] = category_totals
        context['selected_month'] = selected_month
        context['month_param'] = month_param
        
        return context


class ExpenseDetailView(LoginRequiredMixin, DetailView):
    """Vista para mostrar detalles del gasto"""
    model = Expense
    template_name = 'core/expense_detail.html'
    context_object_name = 'expense'
    
    def get_queryset(self):
        return Expense.objects.filter(category__user=self.request.user)


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear nuevos gastos"""
    model = Expense
    form_class = ExpenseForm
    template_name = 'core/expense_form.html'
    success_url = reverse_lazy('core:expense_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtrar categorías por mes si se proporciona
        month_param = self.request.GET.get('month')
        categories_queryset = Category.objects.filter(user=self.request.user)
        
        if month_param:
            try:
                month_date = datetime.strptime(month_param, '%Y-%m').date()
                categories_queryset = categories_queryset.filter(month__year=month_date.year, month__month=month_date.month)
            except ValueError:
                pass
        
        form.fields['category'].queryset = categories_queryset
        return form
    
    def get_success_url(self):
        # Mantener el filtro de mes en la URL de redirección
        month_param = self.request.GET.get('month')
        if month_param:
            return f"{reverse_lazy('core:expense_list')}?month={month_param}"
        return reverse_lazy('core:expense_list')
    
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
    
    def get_queryset(self):
        return Expense.objects.filter(category__user=self.request.user)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtrar categorías por mes si se proporciona
        month_param = self.request.GET.get('month')
        categories_queryset = Category.objects.filter(user=self.request.user)
        
        if month_param:
            try:
                month_date = datetime.strptime(month_param, '%Y-%m').date()
                categories_queryset = categories_queryset.filter(month__year=month_date.year, month__month=month_date.month)
            except ValueError:
                pass
        
        form.fields['category'].queryset = categories_queryset
        return form
    
    def get_success_url(self):
        # Mantener el filtro de mes en la URL de redirección
        month_param = self.request.GET.get('month')
        if month_param:
            return f"{reverse_lazy('core:expense_list')}?month={month_param}"
        return reverse_lazy('core:expense_list')
    
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
    
    def get_queryset(self):
        return Expense.objects.filter(category__user=self.request.user)
    
    def get_success_url(self):
        # Mantener el filtro de mes en la URL de redirección
        month_param = self.request.GET.get('month')
        if month_param:
            return f"{reverse_lazy('core:expense_list')}?month={month_param}"
        return reverse_lazy('core:expense_list')
    
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
    
    def get_queryset(self):
        queryset = Category.objects.filter(user=self.request.user)
        
        # Filtrar por mes si se proporciona
        month_param = self.request.GET.get('month')
        if month_param:
            try:
                month_date = datetime.strptime(month_param, '%Y-%m').date()
                queryset = queryset.filter(month__year=month_date.year, month__month=month_date.month)
            except ValueError:
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el mes seleccionado
        month_param = self.request.GET.get('month')
        selected_month = None
        if month_param:
            try:
                selected_month = datetime.strptime(month_param, '%Y-%m').date()
            except ValueError:
                pass
        
        # Get categories with total spent
        categories_with_totals = Category.objects.filter(user=self.request.user)
        if selected_month:
            categories_with_totals = categories_with_totals.filter(month__year=selected_month.year, month__month=selected_month.month)
        
        categories_with_totals = categories_with_totals.annotate(
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
        context['selected_month'] = selected_month
        context['month_param'] = month_param
        
        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear nuevas categorías"""
    model = Category
    form_class = CategoryForm
    template_name = 'core/category_form.html'
    success_url = reverse_lazy('core:category_list')
    
    def get_success_url(self):
        # Mantener el filtro de mes en la URL de redirección
        month_param = self.request.GET.get('month')
        if month_param:
            return f"{reverse_lazy('core:category_list')}?month={month_param}"
        return reverse_lazy('core:category_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, '¡Categoría creada exitosamente!')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar categorías existentes"""
    model = Category
    form_class = CategoryForm
    template_name = 'core/category_form.html'
    success_url = reverse_lazy('core:category_list')
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        # Mantener el filtro de mes en la URL de redirección
        month_param = self.request.GET.get('month')
        if month_param:
            return f"{reverse_lazy('core:category_list')}?month={month_param}"
        return reverse_lazy('core:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, '¡Categoría actualizada exitosamente!')
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar categorías"""
    model = Category
    template_name = 'core/category_confirm_delete.html'
    success_url = reverse_lazy('core:category_list')
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        # Mantener el filtro de mes en la URL de redirección
        month_param = self.request.GET.get('month')
        if month_param:
            return f"{reverse_lazy('core:category_list')}?month={month_param}"
        return reverse_lazy('core:category_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '¡Categoría eliminada exitosamente!')
        return super().delete(request, *args, **kwargs)


# Vista del Dashboard
def dashboard(request):
    """Vista del dashboard con resumen de gastos"""
    # Obtener el mes seleccionado
    month_param = request.GET.get('month')
    selected_month = None
    if month_param:
        try:
            selected_month = datetime.strptime(month_param, '%Y-%m').date()
        except ValueError:
            pass
    
    # Filtrar gastos por mes si se selecciona
    expenses_queryset = Expense.objects.filter(category__user=request.user)
    if selected_month:
        expenses_queryset = expenses_queryset.filter(date__year=selected_month.year, date__month=selected_month.month)
    
    total_expenses = expenses_queryset.aggregate(total=Sum('amount'))['total'] or 0
    
    # Filtrar categorías por mes si se selecciona
    categories_queryset = Category.objects.filter(user=request.user)
    if selected_month:
        categories_queryset = categories_queryset.filter(month__year=selected_month.year, month__month=selected_month.month)
    
    total_budget = categories_queryset.aggregate(total=Sum('budget'))['total'] or 0
    remaining_budget = total_budget - total_expenses
    
    category_summary = categories_queryset.annotate(
        total_spent=Sum('expenses__amount')
    ).values('name', 'budget', 'total_spent')
    
    recent_expenses = expenses_queryset.select_related('category').order_by('-date')[:5]
    
    context = {
        'total_expenses': total_expenses,
        'total_budget': total_budget,
        'remaining_budget': remaining_budget,
        'category_summary': category_summary,
        'recent_expenses': recent_expenses,
        'selected_month': selected_month,
        'month_param': month_param,
    }
    
    return render(request, 'core/dashboard.html', context)
