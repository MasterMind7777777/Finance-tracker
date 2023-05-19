from django import forms
from tempus_dominus.widgets import DateTimePicker
from .models import Transaction, Category

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['title', 'description', 'amount', 'category', 'date']
        widgets = {
            'date': DateTimePicker(
                options={
                    'useCurrent': True,
                    'format': 'YYYY-MM-DD HH:mm',
                },
                attrs={
                    'append': 'fa fa-calendar',
                }
            ),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type']
