from django.shortcuts import render
from django.db.models import F
from inventory.models import GroceryItem
from django.utils import timezone
from datetime import timedelta

def home(request):
    """Home page with overview stats and quick actions."""
    items = GroceryItem.objects.all()
    today = timezone.now().date()
    
    # Calculate stats
    total_items = items.count()
    low_stock_count = items.filter(quantity__lte=F('low_stock_threshold')).count()
    expiring_soon_count = items.filter(
        expiry_date__gte=today,
        expiry_date__lte=today + timedelta(days=7)
    ).count()
    total_value = sum(item.current_value() for item in items)
    
    # Get recent items (last 5 added)
    recent_items = items.order_by('-id')[:5]
    
    return render(request, 'home.html', {
        'total_items': total_items,
        'low_stock_count': low_stock_count,
        'expiring_soon_count': expiring_soon_count,
        'total_value': total_value,
        'recent_items': recent_items,
    })
