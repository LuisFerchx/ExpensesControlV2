from django import forms
from .models import Expense, Category


class ExpenseForm(forms.ModelForm):
    """Formulario para crear y actualizar objetos Gasto"""
    
    class Meta:
        model = Expense
        fields = ['name', 'amount', 'category', 'date']
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