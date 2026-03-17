from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    budget = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Presupuesto"
    )
    user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, verbose_name="Usuario", null=True, blank=True
    )

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name


class Card(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    type = models.CharField(
        max_length=100,
        verbose_name="Tipo",
        choices=[("debit", "debit"), ("credit", "credit")],
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, verbose_name="Usuario", null=True, blank=True
    )
    mail = models.EmailField(
        verbose_name="Correo electrónico Asociado", null=True, blank=True
    )
    mail_subject = models.CharField(
        verbose_name="Asunto del correo", null=True, blank=True
    )
    cut_off_day = models.IntegerField(verbose_name="Día de corte", default=1)
    payment_day = models.IntegerField(verbose_name="Día de pago", default=1)
    expiration_date = models.DateField(
        null=True, blank=True, verbose_name="Fecha de expiración"
    )
    color = models.CharField(max_length=7, default="#007bff", verbose_name="Color")

    class Meta:
        verbose_name = "Tarjeta"
        verbose_name_plural = "Tarjetas"

    def __str__(self):
        return self.name


class Expense(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="expenses",
        verbose_name="Categoría",
    )
    type = models.CharField(
        max_length=100,
        verbose_name="Tipo",
        choices=[
            ("card", "Tarjeta"),
            ("cash", "Efectivo"),
            ("other", "Otro"),
        ],
        blank=True,
        null=True,
    )
    date = models.DateField(null=True, blank=True, verbose_name="Fecha")
    card = models.ForeignKey(
        Card,
        on_delete=models.SET_NULL,
        verbose_name="Tarjeta",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"

    def __str__(self):
        return f"{self.name} - {self.amount}"
