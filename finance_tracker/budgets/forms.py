from django import forms
from transactions.models import Category

class CategoryBudgetForm(forms.Form):
    category = forms.ModelChoiceField(queryset=None)
    budget_limit = forms.DecimalField(min_value=0)

    def __init__(self, user, category_type, *args, **kwargs):
        super(CategoryBudgetForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user, type=category_type)