from django.contrib import admin
from .models import Category, Transaction
from django import forms


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

    id = forms.IntegerField(required=False)  # Make the 'id' field optional

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = ('id', 'name', 'user', 'type')

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('id') is not None:  # If 'id' is provided in the form
            obj.id = form.cleaned_data['id']  # Use the provided 'id'
        elif not obj.id:  # If 'id' is not set (creating a new object)
            obj.id = None  # Reset 'id' to None to allow auto-generation
        super().save_model(request, obj, form, change)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'amount', 'category', 'date')
