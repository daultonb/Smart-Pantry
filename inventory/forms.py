from django import forms
from .models import GroceryItem, ConsumptionLog

class GroceryItemForm(forms.ModelForm):
    class Meta:
        model = GroceryItem
        fields = ['name', 'category', 'total_portions', 'remaining_portions', 'low_stock_threshold', 'price', 'expiry_date']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ConsumptionForm(forms.ModelForm):
    class Meta:
        model = ConsumptionLog
        fields = ['portions_consumed', 'calories', 'protein', 'carbs', 'fat']
        widgets = {
            'portions_consumed': forms.NumberInput(attrs={'type': 'number', 'min': '1'}),
            'calories': forms.NumberInput(attrs={'type': 'number', 'step': '0.1'}),
            'protein': forms.NumberInput(attrs={'type': 'number', 'step': '0.1'}),
            'carbs': forms.NumberInput(attrs={'type': 'number', 'step': '0.1'}),
            'fat': forms.NumberInput(attrs={'type': 'number', 'step': '0.1'}),
        }