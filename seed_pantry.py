import os
import django
from datetime import date, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_pantry.settings')
django.setup()

from inventory.models import GroceryItem

def seed_data():
    # Clear existing data to avoid duplicates
    GroceryItem.objects.all().delete()
    print('Clearing existing items...')

    test_items = [
        # 1. Healthy & Full
        {
            'name': 'Greek Yogurt',
            'category': 'Dairy',
            'total_portions': 10,
            'remaining_portions': 10,
            'low_stock_threshold': 3,
            'price': 5.99,
            'expiry_date': date.today() + timedelta(days=14),
        },
        # 2. Low Stock (Should appear on Shopping List)
        {
            'name': 'Chicken Breast',
            'category': 'Meat',
            'total_portions': 5,
            'remaining_portions': 2,
            'low_stock_threshold': 3,
            'price': 12.50,
            'expiry_date': date.today() + timedelta(days=5),
        },
        # 3. Out of Stock (Should appear on Shopping List + 'Out of Stock' badge)
        {
            'name': 'Avocados',
            'category': 'Produce',
            'total_portions': 4,
            'remaining_portions': 0,
            'low_stock_threshold': 2,
            'price': 4.00,
            'expiry_date': date.today() + timedelta(days=3),
        },
        # 4. Expired (Should be Red and Bold)
        {
            'name': 'Fresh Spinach',
            'category': 'Produce',
            'total_portions': 1,
            'remaining_portions': 1,
            'low_stock_threshold': 1,
            'price': 3.50,
            'expiry_date': date.today() - timedelta(days=2),
        },
        # 5. Near Expiry (Should be Bold)
        {
            'name': 'Whole Milk',
            'category': 'Dairy',
            'total_portions': 8,
            'remaining_portions': 4,
            'low_stock_threshold': 2,
            'price': 3.80,
            'expiry_date': date.today() + timedelta(days=2),
        },
        # 6. Bulk item (Test progress bar)
        {
            'name': 'Brown Rice',
            'category': 'Grains',
            'total_portions': 100,
            'remaining_portions': 45,
            'low_stock_threshold': 20,
            'price': 15.00,
            'expiry_date': date.today() + timedelta(days=365),
        },
    ]

    for item_data in test_items:
        GroceryItem.objects.create(**item_data)
        print(f"Created: {item_data['name']}")

    print('\nSuccessfully seeded the pantry with test data!')

if __name__ == '__main__':
    seed_data()