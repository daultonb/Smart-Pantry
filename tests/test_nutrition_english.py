"""
Test to verify that nutrition search returns only English results.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inventory.services.nutrition_service import NutritionService

def test_is_english_text():
    """Test the is_english_text method."""
    # English text should return True
    assert NutritionService.is_english_text("Apple") == True
    assert NutritionService.is_english_text("Chicken Breast") == True
    assert NutritionService.is_english_text("Ramen Noodles") == True
    
    # Non-English text should return False
    assert NutritionService.is_english_text("ラーメン") == False
    assert NutritionService.is_english_text("パスタ") == False
    assert NutritionService.is_english_text("意大利面") == False
    
    # Mixed text with mostly non-ASCII should return False
    assert NutritionService.is_english_text("Ramen ラーメン") == False
    
    print("✓ is_english_text tests passed!")

def test_search_returns_english():
    """Test that search_by_name returns only English results."""
    # Test with a common food item
    result = NutritionService.search_by_name("noodle", limit=5)
    
    print(f"\nSearch results for 'noodle':")
    print(f"Number of results: {len(result.get('products', []))}")
    
    for product in result.get('products', []):
        name = product.get('name', '')
        print(f"  - {name}")
        
        # Check that the product name is English
        is_english = NutritionService.is_english_text(name)
        print(f"    Is English: {is_english}")
        assert is_english, f"Product name '{name}' is not English!"
    
    print("\n✓ All products returned are in English!")

def test_search_various_foods():
    """Test search with various food items."""
    test_queries = [
        "apple",
        "chicken",
        "rice",
        "pasta",
        "bread"
    ]
    
    for query in test_queries:
        print(f"\nSearching for '{query}':")
        result = NutritionService.search_by_name(query, limit=3)
        products = result.get('products', [])
        
        for product in products:
            name = product.get('name', '')
            is_english = NutritionService.is_english_text(name)
            status = "✓" if is_english else "✗"
            print(f"  {status} {name} (English: {is_english})")
            assert is_english, f"Product name '{name}' is not English!"

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Nutrition Service English Filter")
    print("=" * 60)
    
    test_is_english_text()
    test_search_returns_english()
    test_search_various_foods()
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)