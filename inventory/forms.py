from django import forms
from .models import GroceryItem, ConsumptionLog, Recipe, RecipeIngredient, UNIT_CHOICES

class GroceryItemForm(forms.ModelForm):
    """Form for adding/editing grocery items with multi-unit support."""
    class Meta:
        model = GroceryItem
        fields = ['name', 'category', 'quantity', 'total_quantity', 'unit', 'low_stock_threshold', 'price', 'expiry_date', 'store']
        widgets = {
            'quantity': forms.NumberInput(attrs={'type': 'number', 'step': '0.01', 'min': '0'}),
            'total_quantity': forms.NumberInput(attrs={'type': 'number', 'step': '0.01', 'min': '0'}),
            'low_stock_threshold': forms.NumberInput(attrs={'type': 'number', 'min': '0'}),
            'price': forms.NumberInput(attrs={'type': 'number', 'step': '0.01', 'min': '0'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'store': forms.TextInput(attrs={'placeholder': 'e.g., Walmart, Costco, Trader Joe\'s'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values for new items
        if not self.instance.pk:
            self.initial['quantity'] = 1
            self.initial['total_quantity'] = 1
            self.initial['low_stock_threshold'] = 1


class ConsumptionForm(forms.Form):
    """Form for consuming items with multi-unit support and nutrition search."""
    amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'type': 'number', 'step': '0.01', 'min': '0.01'})
    )
    product_name = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search for product (e.g., "cereal", "milk")',
            'class': 'product-search-input'
        })
    )
    calories = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={'type': 'number', 'step': '0.1', 'min': '0'})
    )
    protein = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={'type': 'number', 'step': '0.1', 'min': '0'})
    )
    carbs = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={'type': 'number', 'step': '0.1', 'min': '0'})
    )
    fat = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={'type': 'number', 'step': '0.1', 'min': '0'})
    )


class RecipeForm(forms.ModelForm):
    """Form for adding/editing recipes."""
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'instructions']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Brief description of this recipe...'}),
            'instructions': forms.Textarea(attrs={'rows': 8, 'placeholder': 'Step-by-step cooking instructions...'}),
        }


class RecipeIngredientForm(forms.ModelForm):
    """Form for adding ingredients to a recipe."""
    class Meta:
        model = RecipeIngredient
        fields = ['item', 'required_amount']
        widgets = {
            'required_amount': forms.NumberInput(attrs={'type': 'number', 'step': '0.01', 'min': '0.01'}),
        }


class RecipeIngredientFormSet(forms.BaseFormSet):
    """Dynamic formset for recipe ingredients."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.forms:
            for form in self.forms:
                # Filter items that have quantity available
                form.fields['item'].queryset = GroceryItem.objects.filter(quantity__gt=0)
