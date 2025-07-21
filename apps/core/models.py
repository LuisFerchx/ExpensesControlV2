from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    budget = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Presupuesto")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Usuario", null=True, blank=True)
    month = models.DateField(null=True, blank=True, verbose_name="Mes")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name

class Expense(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='expenses', verbose_name="Categoría")
    date = models.DateField(null=True, blank=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"

    def __str__(self):
        return f"{self.name} - {self.amount}"