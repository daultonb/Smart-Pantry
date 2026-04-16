import os
import django
from datetime import date, timedelta, datetime
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_pantry.settings')
django.setup()

from inventory.models import GroceryItem, PriceHistory, Recipe, RecipeIngredient
from decimal import Decimal

def seed_data():
    # Clear existing data to avoid duplicates
    GroceryItem.objects.all().delete()
    PriceHistory.objects.all().delete()
    print('Clearing existing items...')

    test_items = [
        # 1. Healthy & Full
        {
            'name': 'Greek Yogurt',
            'category': 'Dairy',
            'quantity': Decimal('10.00'),
            'total_quantity': Decimal('10.00'),
            'unit': 'cups',
            'total_portions': 10,
            'remaining_portions': 10,
            'low_stock_threshold': 3,
            'price': 5.99,
            'expiry_date': date.today() + timedelta(days=14),
            'store': 'Walmart',
        },
        # 2. Low Stock (Should appear on Shopping List)
        {
            'name': 'Chicken Breast',
            'category': 'Meat',
            'quantity': Decimal('2.00'),
            'total_quantity': Decimal('5.00'),
            'unit': 'pounds',
            'total_portions': 5,
            'remaining_portions': 2,
            'low_stock_threshold': 3,
            'price': 12.50,
            'expiry_date': date.today() + timedelta(days=5),
            'store': 'Costco',
        },
        # 3. Out of Stock (Should appear on Shopping List + 'Out of Stock' badge)
        {
            'name': 'Avocados',
            'category': 'Produce',
            'quantity': Decimal('0.00'),
            'total_quantity': Decimal('4.00'),
            'unit': 'pieces',
            'total_portions': 4,
            'remaining_portions': 0,
            'low_stock_threshold': 2,
            'price': 4.00,
            'expiry_date': date.today() + timedelta(days=3),
            'store': 'Trader Joe\'s',
        },
        # 4. Expired (Should be Red and Bold)
        {
            'name': 'Fresh Spinach',
            'category': 'Produce',
            'quantity': Decimal('1.00'),
            'total_quantity': Decimal('1.00'),
            'unit': 'pounds',
            'total_portions': 1,
            'remaining_portions': 1,
            'low_stock_threshold': 1,
            'price': 3.50,
            'expiry_date': date.today() - timedelta(days=2),
            'store': 'Whole Foods',
        },
        # 5. Near Expiry (Should be Bold)
        {
            'name': 'Whole Milk',
            'category': 'Dairy',
            'quantity': Decimal('4.00'),
            'total_quantity': Decimal('8.00'),
            'unit': 'cups',
            'total_portions': 8,
            'remaining_portions': 4,
            'low_stock_threshold': 2,
            'price': 3.80,
            'expiry_date': date.today() + timedelta(days=2),
            'store': 'Safeway',
        },
        # 6. Bulk item (Test progress bar)
        {
            'name': 'Brown Rice',
            'category': 'Grains',
            'quantity': Decimal('45.00'),
            'total_quantity': Decimal('100.00'),
            'unit': 'cups',
            'total_portions': 100,
            'remaining_portions': 45,
            'low_stock_threshold': 20,
            'price': 15.00,
            'expiry_date': date.today() + timedelta(days=365),
            'store': 'Costco',
        },
        # 7. Pasta for recipe testing
        {
            'name': 'Penne Pasta',
            'category': 'Grains',
            'quantity': Decimal('5.00'),
            'total_quantity': Decimal('5.00'),
            'unit': 'pounds',
            'total_portions': 5,
            'remaining_portions': 5,
            'low_stock_threshold': 2,
            'price': 2.99,
            'expiry_date': date.today() + timedelta(days=180),
            'store': 'Walmart',
        },
        # 8. Tomato Sauce for recipe testing
        {
            'name': 'Marinara Sauce',
            'category': 'Condiments',
            'quantity': Decimal('3.00'),
            'total_quantity': Decimal('3.00'),
            'unit': 'cans',
            'total_portions': 3,
            'remaining_portions': 3,
            'low_stock_threshold': 1,
            'price': 8.97,
            'expiry_date': date.today() + timedelta(days=90),
            'store': 'Safeway',
        },
        # 9. Parmesan Cheese for recipe testing
        {
            'name': 'Parmesan Cheese',
            'category': 'Dairy',
            'quantity': Decimal('1.00'),
            'total_quantity': Decimal('1.00'),
            'unit': 'pounds',
            'total_portions': 1,
            'remaining_portions': 1,
            'low_stock_threshold': 1,
            'price': 6.99,
            'expiry_date': date.today() + timedelta(days=60),
            'store': 'Whole Foods',
        },
    ]

    created_items = []
    for item_data in test_items:
        item = GroceryItem.objects.create(**item_data)
        created_items.append(item)
        print(f"Created: {item_data['name']}")

    # Create PriceHistory entries for each item with historical data
    # This will populate the analytics charts with meaningful data
    price_history_data = [
        # Greek Yogurt - price fluctuations over 30 days
        {'item': created_items[0], 'old_price': 4.99, 'new_price': 5.49, 'days_ago': 30},
        {'item': created_items[0], 'old_price': 5.49, 'new_price': 5.99, 'days_ago': 20},
        {'item': created_items[0], 'old_price': 5.99, 'new_price': 5.79, 'days_ago': 10},
        {'item': created_items[0], 'old_price': 5.79, 'new_price': 5.99, 'days_ago': 3},
        
        # Chicken Breast - price increase trend
        {'item': created_items[1], 'old_price': 10.99, 'new_price': 11.50, 'days_ago': 28},
        {'item': created_items[1], 'old_price': 11.50, 'new_price': 12.00, 'days_ago': 18},
        {'item': created_items[1], 'old_price': 12.00, 'new_price': 12.50, 'days_ago': 8},
        
        # Avocados - seasonal price variation
        {'item': created_items[2], 'old_price': 3.50, 'new_price': 3.75, 'days_ago': 25},
        {'item': created_items[2], 'old_price': 3.75, 'new_price': 4.25, 'days_ago': 15},
        {'item': created_items[2], 'old_price': 4.25, 'new_price': 4.00, 'days_ago': 5},
        
        # Fresh Spinach - stable price
        {'item': created_items[3], 'old_price': 3.25, 'new_price': 3.50, 'days_ago': 22},
        {'item': created_items[3], 'old_price': 3.50, 'new_price': 3.50, 'days_ago': 12},
        
        # Whole Milk - slight increase
        {'item': created_items[4], 'old_price': 3.50, 'new_price': 3.65, 'days_ago': 27},
        {'item': created_items[4], 'old_price': 3.65, 'new_price': 3.80, 'days_ago': 14},
        
        # Brown Rice - price decrease
        {'item': created_items[5], 'old_price': 16.99, 'new_price': 15.99, 'days_ago': 24},
        {'item': created_items[5], 'old_price': 15.99, 'new_price': 15.00, 'days_ago': 11},
    ]

    for ph_data in price_history_data:
        timestamp = timezone.now() - timedelta(days=ph_data['days_ago'])
        PriceHistory.objects.create(
            item=ph_data['item'],
            old_price=ph_data['old_price'],
            new_price=ph_data['new_price'],
            timestamp=timestamp
        )

    print(f'\nCreated {len(price_history_data)} price history entries')
    
    # Create sample recipes for testing Feature #2
    print('\nCreating sample recipes...')
    
    # Recipe 1: Pasta with Marinara
    pasta_recipe = Recipe.objects.create(
        name='Pasta with Marinara',
        description='Simple and delicious pasta dish',
        instructions='1. Boil pasta according to package directions.\n2. Heat marinara sauce in a pan.\n3. Combine pasta with sauce.\n4. Top with parmesan cheese.'
    )
    RecipeIngredient.objects.create(recipe=pasta_recipe, item=created_items[6], required_amount=Decimal('1.00'))
    RecipeIngredient.objects.create(recipe=pasta_recipe, item=created_items[7], required_amount=Decimal('1.00'))
    RecipeIngredient.objects.create(recipe=pasta_recipe, item=created_items[8], required_amount=Decimal('0.25'))
    print(f"Created recipe: {pasta_recipe.name}")
    
    # Recipe 2: Greek Yogurt Bowl
    yogurt_recipe = Recipe.objects.create(
        name='Greek Yogurt Bowl',
        description='Healthy breakfast bowl',
        instructions='1. Scoop yogurt into a bowl.\n2. Add toppings of your choice.\n3. Enjoy!'
    )
    RecipeIngredient.objects.create(recipe=yogurt_recipe, item=created_items[0], required_amount=Decimal('1.00'))
    print(f"Created recipe: {yogurt_recipe.name}")
    
    print('\nSuccessfully seeded the pantry with test data and recipes!')

if __name__ == '__main__':
    seed_data()