from django import forms
from .models import Expense, Category, Card
from datetime import datetime, date


class ExpenseForm(forms.ModelForm):
    """Formulario para crear y actualizar objetos Gasto"""
    
    class Meta:
        model = Expense
        fields = ['name', 'amount', 'category', 'type', 'card', 'date']
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
            'card': forms.Select(attrs={
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

class CardForm(forms.ModelForm):
    """Formulario para crear y actualizar objetos Tarjeta"""
    
    class Meta:
        model = Card
        fields = ['name', 'type', 'color', 'mail', 'mail_subject', 'cut_off_day', 'payment_day', 'expiration_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la tarjeta'
            }),
            'type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control form-control-color',
                'type': 'color',
                'style': 'max-width: 100%; height: calc(2.25rem + 2px);'
            }),
            'mail': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'mail_subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Asunto del correo para notificaciones'
            }),
            'cut_off_day': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '31'
            }),
            'payment_day': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '31'
            }),
            'expiration_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }