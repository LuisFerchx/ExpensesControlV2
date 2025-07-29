from django import forms
from .models import Expense, Category
from datetime import datetime, date


class ExpenseForm(forms.ModelForm):
    """Formulario para crear y actualizar objetos Gasto"""
    
    class Meta:
        model = Expense
        fields = ['name', 'amount', 'category', 'type', 'date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del gasto'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer el campo fecha requerido para nuevos gastos
        if not self.instance.pk:
            self.fields['date'].required = True


class CategoryForm(forms.ModelForm):
    """Formulario para crear y actualizar objetos Categoría"""
    
    # Campo personalizado para mes
    month_input = forms.CharField(
        label="Mes",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'month',
            'placeholder': 'Selecciona un mes'
        }),
        help_text="Selecciona el mes para el cual se aplicará esta categoría y presupuesto."
    )
    
    class Meta:
        model = Category
        fields = ['name', 'budget']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la categoría'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            })
        } 
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer el valor inicial del campo month_input
        if self.instance.pk and self.instance.month:
            self.fields['month_input'].initial = self.instance.month.strftime('%Y-%m')
    
    def clean_month_input(self):
        """Validación personalizada para el campo month_input"""
        month_value = self.cleaned_data.get('month_input')
        if not month_value:
            return None
        
        try:
            # Parsear YYYY-MM a datetime
            month_date = datetime.strptime(month_value, '%Y-%m')
            # Retornar el primer día del mes
            return month_date.replace(day=1).date()
        except ValueError:
            raise forms.ValidationError("Por favor ingresa un mes válido en formato YYYY-MM (ejemplo: 2024-01)")
    
    def save(self, commit=True):
        """Guardar el formulario y asignar el valor del mes"""
        instance = super().save(commit=False)
        instance.month = self.cleaned_data.get('month_input')
        
        if commit:
            instance.save()
        return instance 