from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, date
from .models import Expense, Category, Card
from .forms import ExpenseForm, CategoryForm, CardForm


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
        
        # Categorías son globales ahora, no se filtran por mes
        categories_queryset = Category.objects.filter(user=self.request.user)
        
        context['categories'] = categories_queryset
        
        # Calcular totales filtrados por mes
        expenses_queryset = Expense.objects.filter(category__user=self.request.user)
        if selected_month:
            expenses_queryset = expenses_queryset.filter(date__year=selected_month.year, date__month=selected_month.month)
        
        context['total_expenses'] = expenses_queryset.aggregate(total=Sum('amount'))['total'] or 0
        
        # Calcular totales por categoría filtrados por mes
        from django.db.models import Q
        category_totals = Category.objects.filter(user=self.request.user)
        
        if selected_month:
            expense_filter = Q(expenses__date__year=selected_month.year, expenses__date__month=selected_month.month)
            category_totals = category_totals.annotate(
                total_spent=Sum('expenses__amount', filter=expense_filter)
            ).values('name', 'budget', 'total_spent')
        else:
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
        form.fields['category'].queryset = Category.objects.filter(user=self.request.user)
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
        form.fields['category'].queryset = Category.objects.filter(user=self.request.user)
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
        return Category.objects.filter(user=self.request.user)
    
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
        
        categories_with_totals = Category.objects.filter(user=self.request.user)
        
        from django.db.models import Q
        if selected_month:
            expense_filter = Q(expenses__date__year=selected_month.year, expenses__date__month=selected_month.month)
            categories_with_totals = categories_with_totals.annotate(
                total_spent=Sum('expenses__amount', filter=expense_filter)
            )
        else:
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
    
    # Filtrar categorías
    categories_queryset = Category.objects.filter(user=request.user)
    
    total_budget = categories_queryset.aggregate(total=Sum('budget'))['total'] or 0
    remaining_budget = total_budget - total_expenses
    
    from django.db.models import Q
    if selected_month:
        expense_filter = Q(expenses__date__year=selected_month.year, expenses__date__month=selected_month.month)
        category_summary = categories_queryset.annotate(
            total_spent=Sum('expenses__amount', filter=expense_filter)
        ).values('name', 'budget', 'total_spent')
    else:
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

# Vistas de Tarjetas
class CardListView(LoginRequiredMixin, ListView):
    """Vista para listar todas las tarjetas"""
    model = Card
    template_name = 'core/card_list.html'
    context_object_name = 'cards'
    ordering = ['name']
    
    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)


class CardCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear nuevas tarjetas"""
    model = Card
    form_class = CardForm
    template_name = 'core/card_form.html'
    success_url = reverse_lazy('core:card_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, '¡Tarjeta creada exitosamente!')
        return super().form_valid(form)


class CardUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar tarjetas existentes"""
    model = Card
    form_class = CardForm
    template_name = 'core/card_form.html'
    success_url = reverse_lazy('core:card_list')
    
    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, '¡Tarjeta actualizada exitosamente!')
        return super().form_valid(form)


class CardDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar tarjetas"""
    model = Card
    template_name = 'core/card_confirm_delete.html'
    success_url = reverse_lazy('core:card_list')
    
    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '¡Tarjeta eliminada exitosamente!')
        return super().delete(request, *args, **kwargs)

class CardSyncListView(LoginRequiredMixin, ListView):
    """Vista para sincronizar gastos de tarjetas de crédito"""
    model = Card
    template_name = 'core/card_sync.html'
    context_object_name = 'cards'
    
    def get_queryset(self):
        return Card.objects.filter(user=self.request.user, type='credit')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el mes y año seleccionado
        month_param = self.request.GET.get('month')
        if not month_param:
            # Por defecto el mes actual
            now = timezone.now()
            month_param = f"{now.year}-{now.month:02d}"
            
        context['month_param'] = month_param
        try:
            year_str, month_str = month_param.split('-')
            context['target_year'] = int(year_str)
            context['target_month'] = int(month_str)
        except ValueError:
            now = timezone.now()
            context['target_year'] = now.year
            context['target_month'] = now.month
            
        return context

@login_required
def sync_card_action(request, pk):
    """Acción para ejecutar la sincronización de una tarjeta específica"""
    if request.method != 'POST':
        return redirect('core:card_sync_list')
        
    card = get_object_or_404(Card, pk=pk, user=request.user)
    
    month_param = request.POST.get('month')
    try:
        if month_param:
            year_str, month_str = month_param.split('-')
            target_year = int(year_str)
            target_month = int(month_str)
        else:
            now = timezone.now()
            target_year = now.year
            target_month = now.month
            
        from .services.expense_sync import sync_card_expenses
        created, msg = sync_card_expenses(card.id, target_month, target_year)
        
        if created > 0:
            messages.success(request, f'¡Sincronización exitosa! {msg}')
        else:
            messages.warning(request, f'No se crearon gastos nuevos. {msg}')
            
    except Exception as e:
        messages.error(request, f'Error durante la sincronización: {str(e)}')
        
    # Redirect back to sync list, preserving the month filter
    url = reverse_lazy('core:card_sync_list')
    if month_param:
        return redirect(f"{url}?month={month_param}")
    return redirect(url)
