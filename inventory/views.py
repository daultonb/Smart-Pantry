from django.shortcuts import render, redirect, get_object_or_404
from .models import GroceryItem, ConsumptionLog
from .forms import GroceryItemForm, ConsumptionForm
from django.utils import timezone
from datetime import timedelta

def pantry_dashboard(request):
    items = GroceryItem.objects.all()
    today = timezone.now().date()
    # Add expiry status to each item object
    for item in items:
        if item.expiry_date:
            item.is_expired = item.expiry_date < today
            item.is_near_expiry = not item.is_expired and (item.expiry_date - today).days <= 3
        else:
            item.is_expired = False
            item.is_near_expiry = False

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
        form = GroceryItemForm(initial={'total_portions': 1, 'remaining_portions': 1, 'low_stock_threshold': 1})
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
            portions = form.cleaned_data['portions_consumed']
            if portions > item.remaining_portions:
                form.add_error('portions_consumed', f'Not enough portions left! Only {item.remaining_portions} remaining.')
            else:
                # 1. Create the log entry
                consumption = form.save(commit=False)
                consumption.item = item
                consumption.save()

                # 2. Decrement inventory
                item.remaining_portions -= portions
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
    low_stock_items = [item for item in all_items if item.remaining_portions <= item.low_stock_threshold]
    return render(request, 'inventory/shopping_list.html', {'items': low_stock_items})

def restock_item(request, pk):
    item = get_object_or_404(GroceryItem, pk=pk)
    if request.method == 'POST':
        form = GroceryItemForm(request.POST, instance=item)
        if form.is_valid():
            updated_item = form.save(commit=False)
            updated_item.remaining_portions = updated_item.total_portions
            updated_item.save()
            return redirect('shopping_list')
    else:
        form = GroceryItemForm(instance=item)
    return render(request, 'inventory/item_form.html', {'form': form, 'action': 'Restock', 'item': item})

