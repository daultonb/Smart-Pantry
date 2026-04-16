from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from django.http import JsonResponse
from .models import GroceryItem, ConsumptionLog, PriceHistory, Recipe, RecipeIngredient
from .forms import GroceryItemForm, ConsumptionForm, RecipeForm, RecipeIngredientForm
from .services.nutrition_service import NutritionService
from django.utils import timezone
from datetime import timedelta, date
from collections import defaultdict
from decimal import Decimal
import json

def pantry_dashboard(request):
    items = GroceryItem.objects.all().order_by('-expiry_date')
    today = timezone.now().date()

    return render(request, 'inventory/dashboard.html', {
        'items': items,
        'today': today
    })

def add_item(request):
    if request.method == 'POST':
        form = GroceryItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pantry_dashboard')
    else:
        form = GroceryItemForm()
    return render(request, 'inventory/item_form.html', {'form': form, 'action': 'Add'})

def edit_item(request, pk):
    item = get_object_or_404(GroceryItem, pk=pk)
    if request.method == 'POST':
        form = GroceryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('pantry_dashboard')
    else:
        form = GroceryItemForm(instance=item)
    return render(request, 'inventory/item_form.html', {'form': form, 'action': 'Edit'})

def delete_item(request, pk):
    item = get_object_or_404(GroceryItem, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('pantry_dashboard')
    return render(request, 'inventory/item_confirm_delete.html', {'item': item})

def consume_item(request, pk):
    item = get_object_or_404(GroceryItem, pk=pk)
    if request.method == 'POST':
        form = ConsumptionForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if amount > item.quantity:
                form.add_error('amount', f'Not enough {item.unit} left! Only {item.quantity} remaining.')
            else:
                # 1. Create the log entry
                consumption = ConsumptionLog(
                    item=item,
                    portions_consumed=int(amount),  # Store as integer for backward compatibility
                    calories=form.cleaned_data.get('calories', 0),
                    protein=form.cleaned_data.get('protein', 0),
                    carbs=form.cleaned_data.get('carbs', 0),
                    fat=form.cleaned_data.get('fat', 0)
                )
                consumption.save()

                # 2. Decrement inventory using new quantity field
                item.quantity = item.quantity - amount
                item.save()

                return redirect('pantry_dashboard')
    else:
        form = ConsumptionForm()

    return render(request, 'inventory/consume_item.html', {
        'form': form,
        'item': item,
        'action': 'Consume'
    })

def shopping_list(request):
    all_items = GroceryItem.objects.all()
    low_stock_items = [item for item in all_items if item.is_low_stock]
    return render(request, 'inventory/shopping_list.html', {'items': low_stock_items})

def restock_item(request, pk):
    item = get_object_or_404(GroceryItem, pk=pk)
    if request.method == 'POST':
        form = GroceryItemForm(request.POST, instance=item)
        if form.is_valid():
            updated_item = form.save(commit=False)
            updated_item.quantity = updated_item.total_quantity
            updated_item.save()
            return redirect('shopping_list')
    else:
        form = GroceryItemForm(instance=item)
    return render(request, 'inventory/item_form.html', {'form': form, 'action': 'Restock', 'item': item})

# Feature #2: Recipe Templates Views
def recipe_dashboard(request):
    """Display all recipes with their ingredients."""
    recipes = Recipe.objects.prefetch_related('ingredients__item').all()
    return render(request, 'inventory/recipe_dashboard.html', {'recipes': recipes})

def add_recipe(request):
    """Create a new recipe."""
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            recipe = form.save()
            # Process ingredients
            ingredient_count = int(request.POST.get('ingredient_count', 0))
            for i in range(ingredient_count):
                item_id = request.POST.get(f'ingredient_{i}_item')
                amount = request.POST.get(f'ingredient_{i}_amount')
                if item_id and amount:
                    try:
                        item = GroceryItem.objects.get(pk=item_id)
                        RecipeIngredient.objects.create(
                            recipe=recipe,
                            item=item,
                            required_amount=Decimal(amount)
                        )
                    except GroceryItem.DoesNotExist:
                        pass
            return redirect('recipe_dashboard')
    else:
        form = RecipeForm()
    available_items = GroceryItem.objects.filter(quantity__gt=0).order_by('name')
    return render(request, 'inventory/recipe_form.html', {
        'form': form, 
        'action': 'Add', 
        'available_items': available_items
    })

def edit_recipe(request, pk):
    """Edit an existing recipe."""
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)
        if form.is_valid():
            recipe = form.save()
            # Delete existing ingredients
            RecipeIngredient.objects.filter(recipe=recipe).delete()
            # Process new ingredients
            ingredient_count = int(request.POST.get('ingredient_count', 0))
            for i in range(ingredient_count):
                item_id = request.POST.get(f'ingredient_{i}_item')
                amount = request.POST.get(f'ingredient_{i}_amount')
                if item_id and amount:
                    try:
                        item = GroceryItem.objects.get(pk=item_id)
                        RecipeIngredient.objects.create(
                            recipe=recipe,
                            item=item,
                            required_amount=Decimal(amount)
                        )
                    except GroceryItem.DoesNotExist:
                        pass
            return redirect('recipe_dashboard')
    else:
        form = RecipeForm(instance=recipe)
    available_items = GroceryItem.objects.filter(quantity__gt=0).order_by('name')
    return render(request, 'inventory/recipe_form.html', {
        'form': form, 
        'action': 'Edit', 
        'recipe': recipe,
        'ingredients': recipe.ingredients.all(),
        'available_items': available_items
    })

def delete_recipe(request, pk):
    """Delete a recipe."""
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        recipe.delete()
        return redirect('recipe_dashboard')
    return render(request, 'inventory/recipe_confirm_delete.html', {'recipe': recipe})

def cook_recipe(request, pk):
    """Cook a recipe - consume all ingredients atomically."""
    recipe = get_object_or_404(Recipe, pk=pk)
    error_message = None
    success_message = None
    
    if request.method == 'POST':
        success, message = recipe.cook()
        if success:
            success_message = message
            return redirect('recipe_dashboard')
        else:
            error_message = message
    
    # Check if recipe can be cooked
    can_cook = recipe.can_cook()
    missing_ingredients = recipe.get_missing_ingredients() if not can_cook else []
    
    return render(request, 'inventory/cook_recipe.html', {
        'recipe': recipe,
        'can_cook': can_cook,
        'missing_ingredients': missing_ingredients,
        'error_message': error_message,
        'success_message': success_message
    })

def analytics(request):
    """Financial Analytics page with charts and data."""
    items = GroceryItem.objects.all()
    
    # Calculate total pantry value
    total_value = sum(item.current_value() for item in items)
    
    # Get time range from query parameter (default: 30 days)
    days_range = int(request.GET.get('days', 30))
    date_range_options = [7, 14, 30, 60]
    
    # Calculate value by category
    value_by_category = defaultdict(float)
    for item in items:
        value_by_category[item.category] += float(item.current_value())
    
    # Calculate value by store
    value_by_store = defaultdict(float)
    for item in items:
        value_by_store[item.store] += float(item.current_value())
    
    # Get price history for items
    price_history_data = PriceHistory.objects.select_related('item').all()
    
    # Prepare chart data for price history per item
    item_price_history = defaultdict(list)
    for ph in price_history_data:
        item_price_history[ph.item.name].append({
            'date': ph.timestamp.strftime('%Y-%m-%d'),
            'price': float(ph.new_price)
        })
    
    # Calculate historical pantry values (on-demand simulation)
    # We'll create snapshots based on price history timestamps
    historical_values = []
    today = timezone.now().date()
    start_date = today - timedelta(days=days_range)
    
    # Get all price history entries within range
    recent_price_history = PriceHistory.objects.filter(
        timestamp__gte=start_date
    ).order_by('timestamp')
    
    # Create daily snapshots
    current_date = start_date
    while current_date <= today:
        # Calculate pantry value as of this date
        # For simplicity, we use current item values but note this is a simulation
        # A true historical calculation would require more complex logic
        day_value = sum(item.current_value() for item in items)
        historical_values.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'value': float(day_value)
        })
        current_date += timedelta(days=1)
    
    context = {
        'total_value': total_value,
        'items_count': len(items),
        'categories_count': len(value_by_category),
        'value_by_category': json.dumps(dict(value_by_category)),
        'value_by_store': json.dumps(dict(value_by_store)),
        'item_price_history': json.dumps(dict(item_price_history)),
        'historical_values': json.dumps(historical_values),
        'days_range': days_range,
        'date_range_options': date_range_options,
    }
    
    return render(request, 'inventory/analytics.html', context)


# Nutrition API endpoints
def nutrition_search_by_name(request):
    """
    AJAX endpoint to search for products by name.
    Returns JSON with product suggestions and nutrition data.
    """
    query = request.GET.get('q', '')
    if not query or len(query) < 2:
        return JsonResponse({'products': [], 'error': 'Search query too short'})
    
    results = NutritionService.search_by_name(query, limit=5)
    products = []
    
    for product in results.get('products', [])[:5]:
        products.append({
            'code': product.get('code', ''),
            'name': product.get('name', ''),
            'brands': ', '.join(product.get('brands', [])) if isinstance(product.get('brands'), list) else product.get('brands', ''),
            'calories': product.get('calories', 0),
            'protein': product.get('protein', 0),
            'carbs': product.get('carbs', 0),
            'fat': product.get('fat', 0),
        })
    
    return JsonResponse({'products': products})


def nutrition_search_by_barcode(request, barcode):
    """
    AJAX endpoint to search for product by barcode.
    Returns JSON with nutrition data.
    """
    nutrition = NutritionService.get_nutrition_with_cache(barcode)
    
    if not nutrition.get('code'):
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    return JsonResponse({
        'code': nutrition.get('code', ''),
        'name': nutrition.get('product_name', ''),
        'brands': nutrition.get('brands', ''),
        'calories': nutrition.get('calories', 0),
        'protein': nutrition.get('protein', 0),
        'carbs': nutrition.get('carbs', 0),
        'fat': nutrition.get('fat', 0),
    })

