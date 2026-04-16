"""
Nutrition Service - Integrates with Open Food Facts API
https://world.openfoodfacts.org/

This service provides methods to search for food products and extract
nutrition data automatically.
Includes a fallback database of common food items for reliability.
"""

import requests
from typing import Dict, List, Optional
from functools import lru_cache

# Simple in-memory cache for nutrition data
class SimpleCache:
    def __init__(self):
        self._cache = {}
    
    def get(self, key: str) -> Optional[Dict]:
        return self._cache.get(key)
    
    def set(self, key: str, value: Dict, timeout: int = 3600):
        self._cache[key] = value

cache = SimpleCache()


class NutritionService:
    """Service for fetching nutrition data from Open Food Facts API."""
    
    BASE_URL = "https://world.openfoodfacts.org"
    HEADERS = {
        'User-Agent': 'SmartPantry/1.0 (smartpantry.app)',
        'Accept': 'application/json'
    }
    CACHE_TIMEOUT = 3600  # 1 hour
    
    # Fallback database of common foods (per 100g)
    # Format: 'common_name': {'name': 'Display Name', 'calories': X, 'protein': X, 'carbs': X, 'fat': X}
    FALLBACK_FOODS = {
        # Fruits
        'apple': {'name': 'Apple', 'calories': 52, 'protein': 0.3, 'carbs': 14, 'fat': 0.2},
        'banana': {'name': 'Banana', 'calories': 89, 'protein': 1.1, 'carbs': 23, 'fat': 0.3},
        'orange': {'name': 'Orange', 'calories': 47, 'protein': 0.9, 'carbs': 12, 'fat': 0.1},
        'grape': {'name': 'Grape', 'calories': 67, 'protein': 0.7, 'carbs': 18, 'fat': 0.2},
        'strawberry': {'name': 'Strawberry', 'calories': 32, 'protein': 0.7, 'carbs': 8, 'fat': 0.3},
        'blueberry': {'name': 'Blueberry', 'calories': 57, 'protein': 0.7, 'carbs': 14, 'fat': 0.3},
        'raspberry': {'name': 'Raspberry', 'calories': 52, 'protein': 1.2, 'carbs': 12, 'fat': 0.7},
        'blackberry': {'name': 'Blackberry', 'calories': 43, 'protein': 1.4, 'carbs': 10, 'fat': 0.5},
        'mango': {'name': 'Mango', 'calories': 60, 'protein': 0.8, 'carbs': 15, 'fat': 0.4},
        'pineapple': {'name': 'Pineapple', 'calories': 50, 'protein': 0.5, 'carbs': 13, 'fat': 0.1},
        'papaya': {'name': 'Papaya', 'calories': 43, 'protein': 0.5, 'carbs': 11, 'fat': 0.3},
        'peach': {'name': 'Peach', 'calories': 39, 'protein': 0.9, 'carbs': 10, 'fat': 0.3},
        'pear': {'name': 'Pear', 'calories': 57, 'protein': 0.4, 'carbs': 15, 'fat': 0.1},
        'plum': {'name': 'Plum', 'calories': 46, 'protein': 0.7, 'carbs': 11, 'fat': 0.3},
        'cherry': {'name': 'Cherry', 'calories': 50, 'protein': 1.1, 'carbs': 12, 'fat': 0.2},
        'kiwi': {'name': 'Kiwi', 'calories': 61, 'protein': 1.1, 'carbs': 15, 'fat': 0.5},
        'lemon': {'name': 'Lemon', 'calories': 29, 'protein': 1.1, 'carbs': 9, 'fat': 0.3},
        'lime': {'name': 'Lime', 'calories': 30, 'protein': 0.7, 'carbs': 11, 'fat': 0.2},
        'watermelon': {'name': 'Watermelon', 'calories': 30, 'protein': 0.6, 'carbs': 8, 'fat': 0.2},
        
        # Vegetables
        'carrot': {'name': 'Carrot', 'calories': 41, 'protein': 0.9, 'carbs': 10, 'fat': 0.2},
        'broccoli': {'name': 'Broccoli', 'calories': 34, 'protein': 2.8, 'carbs': 7, 'fat': 0.4},
        'cauliflower': {'name': 'Cauliflower', 'calories': 25, 'protein': 1.9, 'carbs': 5, 'fat': 0.3},
        'cabbage': {'name': 'Cabbage', 'calories': 25, 'protein': 1.3, 'carbs': 6, 'fat': 0.1},
        'spinach': {'name': 'Spinach', 'calories': 23, 'protein': 2.9, 'carbs': 3.6, 'fat': 0.4},
        'lettuce': {'name': 'Lettuce', 'calories': 15, 'protein': 1.4, 'carbs': 2.9, 'fat': 0.2},
        'tomato': {'name': 'Tomato', 'calories': 18, 'protein': 0.9, 'carbs': 3.9, 'fat': 0.2},
        'cucumber': {'name': 'Cucumber', 'calories': 16, 'protein': 0.7, 'carbs': 4, 'fat': 0.1},
        'celery': {'name': 'Celery', 'calories': 16, 'protein': 0.7, 'carbs': 3, 'fat': 0.2},
        'asparagus': {'name': 'Asparagus', 'calories': 20, 'protein': 2.2, 'carbs': 3.9, 'fat': 0.1},
        'zucchini': {'name': 'Zucchini', 'calories': 17, 'protein': 1.2, 'carbs': 3.1, 'fat': 0.3},
        'bell pepper': {'name': 'Bell Pepper', 'calories': 20, 'protein': 0.9, 'carbs': 4.6, 'fat': 0.2},
        'onion': {'name': 'Onion', 'calories': 40, 'protein': 1.1, 'carbs': 9.3, 'fat': 0.1},
        'garlic': {'name': 'Garlic', 'calories': 149, 'protein': 6.4, 'carbs': 33, 'fat': 0.5},
        'potato': {'name': 'Potato', 'calories': 77, 'protein': 2, 'carbs': 17, 'fat': 0.1},
        'sweet potato': {'name': 'Sweet Potato', 'calories': 86, 'protein': 1.6, 'carbs': 20, 'fat': 0.1},
        'squash': {'name': 'Butternut Squash', 'calories': 45, 'protein': 1, 'carbs': 11, 'fat': 0.1},
        'eggplant': {'name': 'Eggplant', 'calories': 25, 'protein': 1, 'carbs': 6, 'fat': 0.2},
        'mushroom': {'name': 'Mushroom', 'calories': 22, 'protein': 3.1, 'carbs': 3.3, 'fat': 0.3},
        'corn': {'name': 'Corn', 'calories': 86, 'protein': 3.3, 'carbs': 19, 'fat': 1.2},
        'peas': {'name': 'Green Peas', 'calories': 81, 'protein': 5.4, 'carbs': 14, 'fat': 0.4},
        'chickpeas': {'name': 'Chickpeas', 'calories': 164, 'protein': 8.9, 'carbs': 27, 'fat': 2.6},
        'beans': {'name': 'Black Beans', 'calories': 132, 'protein': 8.9, 'carbs': 24, 'fat': 0.5},
        'okra': {'name': 'Okra', 'calories': 33, 'protein': 1.9, 'carbs': 7.5, 'fat': 0.2},
        'beet': {'name': 'Beet', 'calories': 43, 'protein': 1.6, 'carbs': 9.6, 'fat': 0.2},
        'radish': {'name': 'Radish', 'calories': 16, 'protein': 0.7, 'carbs': 3.4, 'fat': 0.1},
        'turnip': {'name': 'Turnip', 'calories': 28, 'protein': 0.9, 'carbs': 6.4, 'fat': 0.1},
        
        # Herbs & Spices
        'parsley': {'name': 'Parsley', 'calories': 36, 'protein': 3, 'carbs': 6.3, 'fat': 0.8},
        'cilantro': {'name': 'Cilantro', 'calories': 23, 'protein': 2.1, 'carbs': 3.7, 'fat': 0.5},
        'basil': {'name': 'Basil', 'calories': 23, 'protein': 3.2, 'carbs': 2.7, 'fat': 0.6},
        'mint': {'name': 'Mint', 'calories': 70, 'protein': 3.8, 'carbs': 14, 'fat': 0.9},
        'ginger': {'name': 'Ginger', 'calories': 80, 'protein': 1.8, 'carbs': 18, 'fat': 0.8},
        'turmeric': {'name': 'Turmeric', 'calories': 354, 'protein': 9.7, 'carbs': 67, 'fat': 9.9},
        'cinnamon': {'name': 'Cinnamon', 'calories': 247, 'protein': 4, 'carbs': 81, 'fat': 1.2},
        'nutmeg': {'name': 'Nutmeg', 'calories': 525, 'protein': 6, 'carbs': 49, 'fat': 36},
        'vanilla': {'name': 'Vanilla Extract', 'calories': 288, 'protein': 0.1, 'carbs': 13, 'fat': 0.1},
        'sugar': {'name': 'Sugar', 'calories': 387, 'protein': 0, 'carbs': 100, 'fat': 0},
        'honey': {'name': 'Honey', 'calories': 304, 'protein': 0.3, 'carbs': 82, 'fat': 0},
        'maple syrup': {'name': 'Maple Syrup', 'calories': 260, 'protein': 0.7, 'carbs': 67, 'fat': 0},
        'salt': {'name': 'Salt', 'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0},
        'pepper': {'name': 'Black Pepper', 'calories': 251, 'protein': 10, 'carbs': 64, 'fat': 3.3},
        'paprika': {'name': 'Paprika', 'calories': 282, 'protein': 14, 'carbs': 54, 'fat': 13},
        'cumin': {'name': 'Cumin', 'calories': 375, 'protein': 18, 'carbs': 44, 'fat': 22},
        'oregano': {'name': 'Oregano', 'calories': 265, 'protein': 9, 'carbs': 69, 'fat': 4.3},
        'thyme': {'name': 'Thyme', 'calories': 276, 'protein': 10, 'carbs': 64, 'fat': 7.4},
        'rosemary': {'name': 'Rosemary', 'calories': 131, 'protein': 4, 'carbs': 21, 'fat': 5.9},
        'sage': {'name': 'Sage', 'calories': 315, 'protein': 11, 'carbs': 61, 'fat': 13},
        'bay leaf': {'name': 'Bay Leaf', 'calories': 313, 'protein': 8, 'carbs': 75, 'fat': 8.4},
        'dill': {'name': 'Dill', 'calories': 43, 'protein': 3.4, 'carbs': 7, 'fat': 1.1},
        'fennel': {'name': 'Fennel', 'calories': 31, 'protein': 1.2, 'carbs': 7, 'fat': 0.2},
        'leek': {'name': 'Leek', 'calories': 61, 'protein': 1.5, 'carbs': 14, 'fat': 0.2},
        'shallot': {'name': 'Shallot', 'calories': 72, 'protein': 2.5, 'carbs': 17, 'fat': 0.2},
        'chives': {'name': 'Chives', 'calories': 110, 'protein': 3.3, 'carbs': 21, 'fat': 1.5},
        'horseradish': {'name': 'Horseradish', 'calories': 19, 'protein': 1.5, 'carbs': 4, 'fat': 0.2},
        'wasabi': {'name': 'Wasabi', 'calories': 109, 'protein': 7.5, 'carbs': 25, 'fat': 0.7},
        
        # Condiments & Sauces
        'soy sauce': {'name': 'Soy Sauce', 'calories': 53, 'protein': 5.6, 'carbs': 4.9, 'fat': 0.1},
        'fish sauce': {'name': 'Fish Sauce', 'calories': 18, 'protein': 3.3, 'carbs': 0.6, 'fat': 0},
        'vinegar': {'name': 'Vinegar', 'calories': 22, 'protein': 0.1, 'carbs': 0.4, 'fat': 0},
        'ketchup': {'name': 'Ketchup', 'calories': 112, 'protein': 1.4, 'carbs': 27, 'fat': 0.2},
        'mustard': {'name': 'Mustard', 'calories': 66, 'protein': 3.7, 'carbs': 5.3, 'fat': 3.3},
        'mayonnaise': {'name': 'Mayonnaise', 'calories': 717, 'protein': 1, 'carbs': 0.6, 'fat': 75},
        'ranch': {'name': 'Ranch Dressing', 'calories': 470, 'protein': 2.5, 'carbs': 4.5, 'fat': 50},
        'caesar': {'name': 'Caesar Dressing', 'calories': 488, 'protein': 2.5, 'carbs': 3.5, 'fat': 52},
        'bbq sauce': {'name': 'BBQ Sauce', 'calories': 172, 'protein': 1.5, 'carbs': 42, 'fat': 0.2},
        'hot sauce': {'name': 'Hot Sauce', 'calories': 11, 'protein': 0.3, 'carbs': 2, 'fat': 0},
        'salsa': {'name': 'Salsa', 'calories': 17, 'protein': 0.5, 'carbs': 3.5, 'fat': 0.2},
        'guacamole': {'name': 'Guacamole', 'calories': 160, 'protein': 2, 'carbs': 9, 'fat': 15},
        'hummus': {'name': 'Hummus', 'calories': 166, 'protein': 5, 'carbs': 14, 'fat': 10},
        'pasta sauce': {'name': 'Pasta Sauce', 'calories': 70, 'protein': 2.5, 'carbs': 13, 'fat': 1.5},
        'marinara': {'name': 'Marinara Sauce', 'calories': 70, 'protein': 2.5, 'carbs': 13, 'fat': 1.5},
        'alfredo': {'name': 'Alfredo Sauce', 'calories': 100, 'protein': 3, 'carbs': 4, 'fat': 9},
        'carbonara': {'name': 'Carbonara Sauce', 'calories': 150, 'protein': 6, 'carbs': 5, 'fat': 12},
        'bolognese': {'name': 'Bolognese Sauce', 'calories': 100, 'protein': 8, 'carbs': 6, 'fat': 5},
        'gravy': {'name': 'Gravy', 'calories': 100, 'protein': 3, 'carbs': 8, 'fat': 6},
        'jam': {'name': 'Jam', 'calories': 263, 'protein': 0.3, 'carbs': 67, 'fat': 0.1},
        'jelly': {'name': 'Jelly', 'calories': 263, 'protein': 0.3, 'carbs': 67, 'fat': 0.1},
        'marmalade': {'name': 'Marmalade', 'calories': 263, 'protein': 0.3, 'carbs': 67, 'fat': 0.1},
        
        # Grains & Bread
        'bread': {'name': 'White Bread', 'calories': 265, 'protein': 9, 'carbs': 49, 'fat': 3.2},
        'whole wheat bread': {'name': 'Whole Wheat Bread', 'calories': 247, 'protein': 13, 'carbs': 41, 'fat': 3.4},
        'bagel': {'name': 'Bagel', 'calories': 250, 'protein': 10, 'carbs': 50, 'fat': 1.7},
        'croissant': {'name': 'Croissant', 'calories': 406, 'protein': 8.2, 'carbs': 45, 'fat': 21},
        'tortilla': {'name': 'Flour Tortilla', 'calories': 298, 'protein': 8.5, 'carbs': 49, 'fat': 7.5},
        'tortilla chip': {'name': 'Tortilla Chip', 'calories': 489, 'protein': 7, 'carbs': 60, 'fat': 24},
        'cracker': {'name': 'Cracker', 'calories': 407, 'protein': 9, 'carbs': 72, 'fat': 10},
        'pretzel': {'name': 'Pretzel', 'calories': 380, 'protein': 10, 'carbs': 80, 'fat': 2.5},
        'popcorn': {'name': 'Popcorn', 'calories': 387, 'protein': 13, 'carbs': 78, 'fat': 4.5},
        'rice': {'name': 'White Rice', 'calories': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3},
        'brown rice': {'name': 'Brown Rice', 'calories': 111, 'protein': 2.6, 'carbs': 23, 'fat': 0.9},
        'pasta': {'name': 'Pasta', 'calories': 131, 'protein': 5, 'carbs': 25, 'fat': 1.1},
        'noodle': {'name': 'Egg Noodle', 'calories': 131, 'protein': 5, 'carbs': 25, 'fat': 1.1},
        'ramen': {'name': 'Ramen Noodles', 'calories': 371, 'protein': 9, 'carbs': 61, 'fat': 11},
        'quinoa': {'name': 'Quinoa', 'calories': 120, 'protein': 4.4, 'carbs': 21, 'fat': 1.9},
        'oats': {'name': 'Oats', 'calories': 389, 'protein': 17, 'carbs': 66, 'fat': 7},
        'barley': {'name': 'Barley', 'calories': 123, 'protein': 2.3, 'carbs': 28, 'fat': 0.4},
        'couscous': {'name': 'Couscous', 'calories': 112, 'protein': 3.8, 'carbs': 23, 'fat': 0.2},
        'bulgur': {'name': 'Bulgur', 'calories': 83, 'protein': 3.1, 'carbs': 19, 'fat': 0.2},
        'wild rice': {'name': 'Wild Rice', 'calories': 101, 'protein': 4, 'carbs': 21, 'fat': 0.3},
        
        # Dairy & Eggs
        'milk': {'name': 'Whole Milk', 'calories': 61, 'protein': 3.2, 'carbs': 4.8, 'fat': 3.3},
        'skim milk': {'name': 'Skim Milk', 'calories': 34, 'protein': 3.4, 'carbs': 5, 'fat': 0.1},
        'yogurt': {'name': 'Plain Yogurt', 'calories': 59, 'protein': 10, 'carbs': 3.6, 'fat': 0.4},
        'greek yogurt': {'name': 'Greek Yogurt', 'calories': 59, 'protein': 10, 'carbs': 3.6, 'fat': 0.4},
        'cheese': {'name': 'Cheddar Cheese', 'calories': 403, 'protein': 25, 'carbs': 1.3, 'fat': 33},
        'mozzarella': {'name': 'Mozzarella', 'calories': 280, 'protein': 28, 'carbs': 2.2, 'fat': 17},
        'parmesan': {'name': 'Parmesan', 'calories': 431, 'protein': 38, 'carbs': 4.1, 'fat': 29},
        'cream cheese': {'name': 'Cream Cheese', 'calories': 342, 'protein': 6, 'carbs': 4, 'fat': 34},
        'cottage cheese': {'name': 'Cottage Cheese', 'calories': 98, 'protein': 11, 'carbs': 3.4, 'fat': 4.3},
        'butter': {'name': 'Butter', 'calories': 717, 'protein': 0.9, 'carbs': 0.1, 'fat': 81},
        'cream': {'name': 'Heavy Cream', 'calories': 340, 'protein': 2.8, 'carbs': 2.8, 'fat': 36},
        'sour cream': {'name': 'Sour Cream', 'calories': 192, 'protein': 2.4, 'carbs': 4.6, 'fat': 19},
        'egg': {'name': 'Egg', 'calories': 155, 'protein': 13, 'carbs': 1.1, 'fat': 11},
        'egg white': {'name': 'Egg White', 'calories': 52, 'protein': 11, 'carbs': 0.7, 'fat': 0.2},
        'egg yolk': {'name': 'Egg Yolk', 'calories': 322, 'protein': 16, 'carbs': 3.6, 'fat': 27},
        
        # Meat & Poultry
        'chicken breast': {'name': 'Chicken Breast', 'calories': 165, 'protein': 31, 'carbs': 0, 'fat': 3.6},
        'chicken thigh': {'name': 'Chicken Thigh', 'calories': 209, 'protein': 26, 'carbs': 0, 'fat': 11},
        'chicken wing': {'name': 'Chicken Wing', 'calories': 203, 'protein': 18, 'carbs': 0, 'fat': 14},
        'turkey': {'name': 'Turkey', 'calories': 135, 'protein': 29, 'carbs': 0, 'fat': 1},
        'duck': {'name': 'Duck', 'calories': 337, 'protein': 19, 'carbs': 0, 'fat': 28},
        'beef': {'name': 'Beef', 'calories': 250, 'protein': 26, 'carbs': 0, 'fat': 15},
        'ground beef': {'name': 'Ground Beef', 'calories': 250, 'protein': 26, 'carbs': 0, 'fat': 15},
        'steak': {'name': 'Steak', 'calories': 271, 'protein': 26, 'carbs': 0, 'fat': 19},
        'pork chop': {'name': 'Pork Chop', 'calories': 231, 'protein': 26, 'carbs': 0, 'fat': 14},
        'pork tenderloin': {'name': 'Pork Tenderloin', 'calories': 143, 'protein': 26, 'carbs': 0, 'fat': 3.5},
        'bacon': {'name': 'Bacon', 'calories': 541, 'protein': 37, 'carbs': 1.4, 'fat': 42},
        'sausage': {'name': 'Sausage', 'calories': 301, 'protein': 12, 'carbs': 0, 'fat': 28},
        'ham': {'name': 'Ham', 'calories': 145, 'protein': 21, 'carbs': 1.5, 'fat': 5},
        'lamb': {'name': 'Lamb', 'calories': 258, 'protein': 25, 'carbs': 0, 'fat': 17},
        'venison': {'name': 'Venison', 'calories': 158, 'protein': 30, 'carbs': 0, 'fat': 3.2},
        
        # Processed Meats
        'pepperoni': {'name': 'Pepperoni', 'calories': 494, 'protein': 20, 'carbs': 0, 'fat': 45},
        'salami': {'name': 'Salami', 'calories': 371, 'protein': 20, 'carbs': 1.2, 'fat': 31},
        'prosciutto': {'name': 'Prosciutto', 'calories': 272, 'protein': 29, 'carbs': 0, 'fat': 17},
        'bologna': {'name': 'Bologna', 'calories': 311, 'protein': 13, 'carbs': 1.2, 'fat': 29},
        'hot dog': {'name': 'Hot Dog', 'calories': 291, 'protein': 12, 'carbs': 27, 'fat': 17},
        'bratwurst': {'name': 'Bratwurst', 'calories': 297, 'protein': 12, 'carbs': 0, 'fat': 28},
        'chorizo': {'name': 'Chorizo', 'calories': 297, 'protein': 12, 'carbs': 0, 'fat': 28},
        'kielbasa': {'name': 'Kielbasa', 'calories': 297, 'protein': 12, 'carbs': 0, 'fat': 28},
        
        # Seafood
        'salmon': {'name': 'Salmon', 'calories': 208, 'protein': 20, 'carbs': 0, 'fat': 13},
        'tuna': {'name': 'Tuna', 'calories': 132, 'protein': 28, 'carbs': 0, 'fat': 1},
        'shrimp': {'name': 'Shrimp', 'calories': 99, 'protein': 24, 'carbs': 0, 'fat': 0.3},
        'cod': {'name': 'Cod', 'calories': 82, 'protein': 18, 'carbs': 0, 'fat': 0.7},
        'tilapia': {'name': 'Tilapia', 'calories': 96, 'protein': 20, 'carbs': 0, 'fat': 1.7},
        'crab': {'name': 'Crab', 'calories': 97, 'protein': 19, 'carbs': 0, 'fat': 1.5},
        'lobster': {'name': 'Lobster', 'calories': 89, 'protein': 19, 'carbs': 0, 'fat': 0.9},
        'clam': {'name': 'Clam', 'calories': 74, 'protein': 16, 'carbs': 2.6, 'fat': 0.4},
        'oyster': {'name': 'Oyster', 'calories': 68, 'protein': 7, 'carbs': 3.9, 'fat': 2.5},
        'mackerel': {'name': 'Mackerel', 'calories': 205, 'protein': 19, 'carbs': 0, 'fat': 14},
        'sardine': {'name': 'Sardine', 'calories': 208, 'protein': 25, 'carbs': 0, 'fat': 11},
        'anchovy': {'name': 'Anchovy', 'calories': 131, 'protein': 20, 'carbs': 0, 'fat': 5},
        
        # Nuts & Seeds
        'peanut': {'name': 'Peanut', 'calories': 567, 'protein': 26, 'carbs': 16, 'fat': 49},
        'almond': {'name': 'Almond', 'calories': 579, 'protein': 21, 'carbs': 22, 'fat': 50},
        'walnut': {'name': 'Walnut', 'calories': 654, 'protein': 15, 'carbs': 14, 'fat': 65},
        'cashew': {'name': 'Cashew', 'calories': 553, 'protein': 18, 'carbs': 30, 'fat': 44},
        'pecan': {'name': 'Pecan', 'calories': 691, 'protein': 9, 'carbs': 14, 'fat': 72},
        'pistachio': {'name': 'Pistachio', 'calories': 560, 'protein': 20, 'carbs': 28, 'fat': 45},
        'sunflower seed': {'name': 'Sunflower Seed', 'calories': 584, 'protein': 21, 'carbs': 20, 'fat': 52},
        'pumpkin seed': {'name': 'Pumpkin Seed', 'calories': 559, 'protein': 30, 'carbs': 11, 'fat': 49},
        'sesame seed': {'name': 'Sesame Seed', 'calories': 573, 'protein': 18, 'carbs': 23, 'fat': 50},
        'chia seed': {'name': 'Chia Seed', 'calories': 486, 'protein': 17, 'carbs': 42, 'fat': 31},
        'flax seed': {'name': 'Flax Seed', 'calories': 534, 'protein': 18, 'carbs': 29, 'fat': 42},
        'macadamia': {'name': 'Macadamia', 'calories': 718, 'protein': 8, 'carbs': 14, 'fat': 76},
        'pine nut': {'name': 'Pine Nut', 'calories': 673, 'protein': 14, 'carbs': 13, 'fat': 68},
        
        # Plant-Based Milks
        'coconut milk': {'name': 'Coconut Milk', 'calories': 230, 'protein': 2.3, 'carbs': 6, 'fat': 24},
        'almond milk': {'name': 'Almond Milk', 'calories': 17, 'protein': 0.6, 'carbs': 0.6, 'fat': 1.1},
        'soy milk': {'name': 'Soy Milk', 'calories': 54, 'protein': 3.3, 'carbs': 6, 'fat': 1.8},
        'oat milk': {'name': 'Oat Milk', 'calories': 47, 'protein': 1, 'carbs': 7, 'fat': 1.5},
        'rice milk': {'name': 'Rice Milk', 'calories': 47, 'protein': 0.3, 'carbs': 10, 'fat': 1},
        
        # Snacks & Sweets
        'chips': {'name': 'Potato Chips', 'calories': 536, 'protein': 7, 'carbs': 53, 'fat': 35},
        'cookie': {'name': 'Chocolate Chip Cookie', 'calories': 488, 'protein': 5, 'carbs': 67, 'fat': 23},
        'cake': {'name': 'Chocolate Cake', 'calories': 371, 'protein': 5, 'carbs': 52, 'fat': 16},
        'pie': {'name': 'Apple Pie', 'calories': 237, 'protein': 2.4, 'carbs': 34, 'fat': 11},
        'donut': {'name': 'Donut', 'calories': 452, 'protein': 5, 'carbs': 51, 'fat': 25},
        'muffin': {'name': 'Blueberry Muffin', 'calories': 350, 'protein': 5, 'carbs': 54, 'fat': 13},
        'cereal': {'name': 'Corn Flakes', 'calories': 357, 'protein': 7, 'carbs': 84, 'fat': 1},
        'granola': {'name': 'Granola', 'calories': 471, 'protein': 13, 'carbs': 65, 'fat': 18},
        'ice cream': {'name': 'Vanilla Ice Cream', 'calories': 207, 'protein': 3.5, 'carbs': 24, 'fat': 11},
        'frozen yogurt': {'name': 'Frozen Yogurt', 'calories': 162, 'protein': 4, 'carbs': 23, 'fat': 5},
        'pudding': {'name': 'Chocolate Pudding', 'calories': 125, 'protein': 3, 'carbs': 20, 'fat': 4},
        'jello': {'name': 'Jello', 'calories': 71, 'protein': 0.7, 'carbs': 17, 'fat': 0},
        'candy': {'name': 'Candy', 'calories': 398, 'protein': 0.4, 'carbs': 97, 'fat': 0.2},
        'chocolate': {'name': 'Dark Chocolate', 'calories': 546, 'protein': 8, 'carbs': 46, 'fat': 31},
        'milk chocolate': {'name': 'Milk Chocolate', 'calories': 535, 'protein': 8, 'carbs': 59, 'fat': 30},
        'white chocolate': {'name': 'White Chocolate', 'calories': 539, 'protein': 5, 'carbs': 58, 'fat': 32},
        
        # Prepared Foods
        'pizza': {'name': 'Pizza', 'calories': 266, 'protein': 11, 'carbs': 33, 'fat': 10},
        'taco': {'name': 'Taco', 'calories': 172, 'protein': 8, 'carbs': 19, 'fat': 7},
        'burrito': {'name': 'Burrito', 'calories': 299, 'protein': 12, 'carbs': 36, 'fat': 11},
        'quesadilla': {'name': 'Quesadilla', 'calories': 298, 'protein': 14, 'carbs': 28, 'fat': 14},
        'enchilada': {'name': 'Enchilada', 'calories': 185, 'protein': 8, 'carbs': 20, 'fat': 8},
        'nachos': {'name': 'Nachos', 'calories': 295, 'protein': 10, 'carbs': 35, 'fat': 13},
        'lasagna': {'name': 'Lasagna', 'calories': 164, 'protein': 12, 'carbs': 15, 'fat': 7},
        'ravioli': {'name': 'Ravioli', 'calories': 140, 'protein': 6, 'carbs': 22, 'fat': 3},
        'gnocchi': {'name': 'Gnocchi', 'calories': 140, 'protein': 4, 'carbs': 28, 'fat': 1},
        'risotto': {'name': 'Risotto', 'calories': 165, 'protein': 5, 'carbs': 28, 'fat': 4},
        'paella': {'name': 'Paella', 'calories': 180, 'protein': 12, 'carbs': 22, 'fat': 5},
        'curry': {'name': 'Chicken Curry', 'calories': 165, 'protein': 15, 'carbs': 8, 'fat': 8},
        'stew': {'name': 'Beef Stew', 'calories': 150, 'protein': 18, 'carbs': 10, 'fat': 6},
        'soup': {'name': 'Chicken Soup', 'calories': 60, 'protein': 6, 'carbs': 6, 'fat': 2},
        'broth': {'name': 'Chicken Broth', 'calories': 10, 'protein': 1, 'carbs': 1, 'fat': 0.5},
        'stock': {'name': 'Vegetable Stock', 'calories': 15, 'protein': 1, 'carbs': 2, 'fat': 0.5},
        'dumpling': {'name': 'Dumpling', 'calories': 165, 'protein': 6, 'carbs': 22, 'fat': 6},
        'spring roll': {'name': 'Spring Roll', 'calories': 292, 'protein': 6, 'carbs': 48, 'fat': 9},
        'egg roll': {'name': 'Egg Roll', 'calories': 292, 'protein': 6, 'carbs': 48, 'fat': 9},
        'hamburger': {'name': 'Hamburger', 'calories': 295, 'protein': 17, 'carbs': 30, 'fat': 13},
        'cheeseburger': {'name': 'Cheeseburger', 'calories': 303, 'protein': 17, 'carbs': 30, 'fat': 14},
        'sandwich': {'name': 'Sandwich', 'calories': 270, 'protein': 12, 'carbs': 30, 'fat': 10},
        'sub': {'name': 'Sub Sandwich', 'calories': 270, 'protein': 12, 'carbs': 30, 'fat': 10},
        'wrap': {'name': 'Wrap', 'calories': 298, 'protein': 8.5, 'carbs': 49, 'fat': 7.5},
        'salad': {'name': 'Caesar Salad', 'calories': 184, 'protein': 5, 'carbs': 7, 'fat': 15},
        'greek salad': {'name': 'Greek Salad', 'calories': 100, 'protein': 4, 'carbs': 8, 'fat': 7},
        'tuna salad': {'name': 'Tuna Salad', 'calories': 150, 'protein': 12, 'carbs': 2, 'fat': 10},
        'chicken salad': {'name': 'Chicken Salad', 'calories': 165, 'protein': 15, 'carbs': 3, 'fat': 10},
        'egg salad': {'name': 'Egg Salad', 'calories': 140, 'protein': 6, 'carbs': 2, 'fat': 11},
        'pasta salad': {'name': 'Pasta Salad', 'calories': 180, 'protein': 5, 'carbs': 25, 'fat': 7},
        'potato salad': {'name': 'Potato Salad', 'calories': 180, 'protein': 3, 'carbs': 18, 'fat': 11},
        'macaroni salad': {'name': 'Macaroni Salad', 'calories': 180, 'protein': 4, 'carbs': 20, 'fat': 9},
        'coleslaw': {'name': 'Coleslaw', 'calories': 180, 'protein': 2, 'carbs': 12, 'fat': 14},
        'deviled egg': {'name': 'Deviled Egg', 'calories': 140, 'protein': 6, 'carbs': 2, 'fat': 11},
        'french fry': {'name': 'French Fry', 'calories': 312, 'protein': 3.4, 'carbs': 41, 'fat': 15},
        'tater tot': {'name': 'Tater Tot', 'calories': 312, 'protein': 3.4, 'carbs': 41, 'fat': 15},
        'hash brown': {'name': 'Hash Brown', 'calories': 312, 'protein': 3.4, 'carbs': 41, 'fat': 15},
        'mashed potato': {'name': 'Mashed Potato', 'calories': 160, 'protein': 3, 'carbs': 20, 'fat': 8},
        'scalloped potato': {'name': 'Scalloped Potato', 'calories': 160, 'protein': 3, 'carbs': 20, 'fat': 8},
        'au gratin': {'name': 'Potato Au Gratin', 'calories': 160, 'protein': 3, 'carbs': 20, 'fat': 8},
        'fries': {'name': 'French Fries', 'calories': 312, 'protein': 3.4, 'carbs': 41, 'fat': 15},
        'wings': {'name': 'Chicken Wings', 'calories': 203, 'protein': 18, 'carbs': 0, 'fat': 14},
        'drumstick': {'name': 'Chicken Drumstick', 'calories': 172, 'protein': 19, 'carbs': 0, 'fat': 10},
        'thigh': {'name': 'Chicken Thigh', 'calories': 209, 'protein': 26, 'carbs': 0, 'fat': 11},
        'wing': {'name': 'Chicken Wing', 'calories': 203, 'protein': 18, 'carbs': 0, 'fat': 14},
        'leg': {'name': 'Chicken Leg', 'calories': 172, 'protein': 19, 'carbs': 0, 'fat': 10},
        'rib': {'name': 'Pork Rib', 'calories': 270, 'protein': 20, 'carbs': 0, 'fat': 20},
        'ribs': {'name': 'Pork Ribs', 'calories': 270, 'protein': 20, 'carbs': 0, 'fat': 20},
        't-bone': {'name': 'T-Bone Steak', 'calories': 271, 'protein': 26, 'carbs': 0, 'fat': 19},
        'ribeye': {'name': 'Ribeye Steak', 'calories': 291, 'protein': 25, 'carbs': 0, 'fat': 21},
        'sirloin': {'name': 'Sirloin Steak', 'calories': 271, 'protein': 26, 'carbs': 0, 'fat': 19},
        'filet': {'name': 'Filet Mignon', 'calories': 184, 'protein': 26, 'carbs': 0, 'fat': 8},
        'burger': {'name': 'Burger', 'calories': 295, 'protein': 17, 'carbs': 30, 'fat': 13},
        'meatball': {'name': 'Meatball', 'calories': 144, 'protein': 12, 'carbs': 3, 'fat': 9},
        'meatloaf': {'name': 'Meatloaf', 'calories': 220, 'protein': 18, 'carbs': 8, 'fat': 13},
        'pork belly': {'name': 'Pork Belly', 'calories': 500, 'protein': 12, 'carbs': 0, 'fat': 50},
        'pork loin': {'name': 'Pork Loin', 'calories': 143, 'protein': 26, 'carbs': 0, 'fat': 3.5},
        'goose': {'name': 'Goose', 'calories': 371, 'protein': 24, 'carbs': 0, 'fat': 30},
        'coconut': {'name': 'Coconut', 'calories': 354, 'protein': 3.3, 'carbs': 15, 'fat': 33},
        'swiss': {'name': 'Swiss Cheese', 'calories': 380, 'protein': 27, 'carbs': 1.4, 'fat': 28},
        'brie': {'name': 'Brie', 'calories': 334, 'protein': 21, 'carbs': 0.5, 'fat': 28},
        'goat cheese': {'name': 'Goat Cheese', 'calories': 364, 'protein': 22, 'carbs': 2.5, 'fat': 29},
        'feta': {'name': 'Feta', 'calories': 264, 'protein': 14, 'carbs': 4.1, 'fat': 21},
        'blue cheese': {'name': 'Blue Cheese', 'calories': 353, 'protein': 21, 'carbs': 2.3, 'fat': 29},
        'provolone': {'name': 'Provolone', 'calories': 343, 'protein': 26, 'carbs': 1.3, 'fat': 26},
        'gouda': {'name': 'Gouda', 'calories': 356, 'protein': 25, 'carbs': 1.2, 'fat': 27},
        'cheddar': {'name': 'Cheddar', 'calories': 403, 'protein': 25, 'carbs': 1.3, 'fat': 33},
        'american': {'name': 'American Cheese', 'calories': 330, 'protein': 23, 'carbs': 1.2, 'fat': 26},
        'pepper jack': {'name': 'Pepper Jack', 'calories': 350, 'protein': 25, 'carbs': 1.2, 'fat': 27},
        'colby': {'name': 'Colby', 'calories': 392, 'protein': 25, 'carbs': 1.2, 'fat': 32},
        'jack': {'name': 'Jack Cheese', 'calories': 343, 'protein': 26, 'carbs': 1.3, 'fat': 26},
        'andouille': {'name': 'Andouille', 'calories': 297, 'protein': 12, 'carbs': 0, 'fat': 28},
        'wurst': {'name': 'Wurst', 'calories': 297, 'protein': 12, 'carbs': 0, 'fat': 28},
        'capicola': {'name': 'Capicola', 'calories': 371, 'protein': 20, 'carbs': 1.2, 'fat': 31},
        'mortadella': {'name': 'Mortadella', 'calories': 301, 'protein': 12, 'carbs': 0, 'fat': 28},
        'parma ham': {'name': 'Parma Ham', 'calories': 272, 'protein': 29, 'carbs': 0, 'fat': 17},
        'speck': {'name': 'Speck', 'calories': 272, 'protein': 29, 'carbs': 0, 'fat': 17},
        'jambon': {'name': 'Jambon', 'calories': 145, 'protein': 21, 'carbs': 1.5, 'fat': 5},
        'schinken': {'name': 'Schinken', 'calories': 145, 'protein': 21, 'carbs': 1.5, 'fat': 5},
        'jamón': {'name': 'Jamón', 'calories': 145, 'protein': 21, 'carbs': 1.5, 'fat': 5},
        'bresaola': {'name': 'Bresaola', 'calories': 272, 'protein': 29, 'carbs': 0, 'fat': 17},
        'coppa': {'name': 'Coppa', 'calories': 371, 'protein': 20, 'carbs': 1.2, 'fat': 31},
        'finocchiona': {'name': 'Finocchiona', 'calories': 371, 'protein': 20, 'carbs': 1.2, 'fat': 31},
        'napoletana': {'name': 'Napoletana', 'calories': 371, 'protein': 20, 'carbs': 1.2, 'fat': 31},
        'genoa': {'name': 'Genoa Salami', 'calories': 371, 'protein': 20, 'carbs': 1.2, 'fat': 31},
        'chicago': {'name': 'Chicago Style', 'calories': 371, 'protein': 20, 'carbs': 1.2, 'fat': 31},
        'hard salami': {'name': 'Hard Salami', 'calories': 371, 'protein': 20, 'carbs': 1.2, 'fat': 31},
        'soft salami': {'name': 'Soft Salami', 'calories': 371, 'protein': 20, 'carbs': 1.2, 'fat': 31},
        'summer sausage': {'name': 'Summer Sausage', 'calories': 371, 'protein': 20, 'carbs': 1.2, 'fat': 31},
        'smoked sausage': {'name': 'Smoked Sausage', 'calories': 301, 'protein': 12, 'carbs': 0, 'fat': 28},
    }
    
    @staticmethod
    def search_by_barcode(barcode: str) -> Dict:
        """
        Search for a product by its barcode.
        
        Args:
            barcode: Product barcode (EAN, UPC, etc.)
            
        Returns:
            Dictionary containing product data or empty dict if not found
        """
        if not barcode or not barcode.strip():
            return {}
            
        url = f"{NutritionService.BASE_URL}/api/v0/product.json"
        params = {'barcodes': barcode.strip()}
        
        try:
            response = requests.get(url, params=params, headers=NutritionService.HEADERS, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching product by barcode: {e}")
            return {}
    
    @staticmethod
    def search_fallback_database(query: str, limit: int = 5) -> List[Dict]:
        """
        Search the fallback database of common foods.
        
        Args:
            query: Product name or description
            limit: Maximum number of results to return
            
        Returns:
            List of matching nutrition data dictionaries
        """
        if not query or not query.strip():
            return []
        
        query_lower = query.lower().strip()
        results = []
        
        # Exact match first
        if query_lower in NutritionService.FALLBACK_FOODS:
            food = NutritionService.FALLBACK_FOODS[query_lower]
            results.append({
                'name': food['name'],
                'brands': 'Common Food',
                'calories': float(food['calories']),
                'protein': float(food['protein']),
                'carbs': float(food['carbs']),
                'fat': float(food['fat']),
                'code': 'fallback'
            })
            return results[:limit]
        
        # Partial match - search for query in food names
        for key, food in NutritionService.FALLBACK_FOODS.items():
            if query_lower in key or key in query_lower:
                results.append({
                    'name': food['name'],
                    'brands': 'Common Food',
                    'calories': float(food['calories']),
                    'protein': float(food['protein']),
                    'carbs': float(food['carbs']),
                    'fat': float(food['fat']),
                    'code': 'fallback'
                })
                if len(results) >= limit:
                    break
        
        return results
    
    @staticmethod
    def is_english_text(text: str) -> bool:
        """
        Check if text is likely English by checking for non-English patterns.
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to be English, False otherwise
        """
        if not text:
            return False
        
        text_lower = text.lower().strip()
        
        # Check for non-ASCII characters (Japanese, Chinese, Korean, etc.)
        non_ascii_count = sum(1 for c in text if ord(c) > 127)
        if non_ascii_count > 0:
            return False
        
        # Check for common French words/patterns
        french_patterns = [
            'pain', 'poulet', 'blanc', 'bio', 'sans', 'avec', 'de', 'les', 'les',
            'compagnie', 'manhattan', 'nature', 'conservation', 'nitrite', 'tranches',
            'céréales', 'graines', 'sucres', 'ajoutés', 'complet', 'grandes',
            'fondue', 'poireaux', 'basmati', 'jacques', 'integrale', 'rigate',
            'mie', 'american', 'sandwich', 'entier', 'entière', 'nouvelle',
            'recette', 'maison', 'traditionnel', 'artisanal', 'ferme', 'paysan'
        ]
        
        for pattern in french_patterns:
            if pattern in text_lower:
                return False
        
        # Check for common German words
        german_patterns = [
            'würstchen', 'bratwurst', 'leberwurst', 'mettwurst', 'kaese',
            'brot', 'fleisch', 'schinken', 'wurst', 'kuchen', 'suppe'
        ]
        
        for pattern in german_patterns:
            if pattern in text_lower:
                return False
        
        # Check for common Spanish words
        spanish_patterns = [
            'queso', 'pan', 'carne', 'pollo', 'pescado', 'jamón', 'empanada',
            'tortilla', 'arroz', 'frijoles', 'salsa', 'guacamole', 'taco'
        ]
        
        for pattern in spanish_patterns:
            if pattern in text_lower:
                return False
        
        # If we get here, text appears to be English
        return True
    
    @staticmethod
    def search_by_name(query: str, limit: int = 5) -> Dict:
        """
        Search for products by name.
        Tries Open Food Facts API first, falls back to local database.
        Filters out non-English results.
        
        Args:
            query: Product name or description
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing search results
        """
        if not query or not query.strip():
            return {'products': []}
        
        # Try multiple API endpoints for better reliability
        endpoints = [
            # Newer API v2 endpoint with English language filter
            {
                'url': "https://world.openfoodfacts.org/api/v0/product.json",
                'params': {
                    'search_terms': query.strip(),
                    'search_simple': 1,
                    'page_size': min(limit, 20),
                    'lc': 'en',  # Language code for English
                    'fields': 'product_name,brands,categories,energy-kcal_100g,proteins_100g,carbohydrates_100g,fat_100g,code'
                }
            },
            # Alternative search endpoint with English filter
            {
                'url': "https://world.openfoodfacts.org/cgi/search.pl",
                'params': {
                    'search_terms': query.strip(),
                    'search_simple': 1,
                    'page_size': min(limit, 20),
                    'json': 1,
                    'lc': 'en',  # Language code for English
                    'fields': 'product_name,brands,categories,energy-kcal_100g,proteins_100g,carbohydrates_100g,fat_100g,code'
                }
            }
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint['url'], params=endpoint['params'], headers=NutritionService.HEADERS, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                # Transform the API response to our expected format
                products = []
                if 'products' in data:
                    for product in data['products'][:limit]:
                        product_name = product.get('product_name', '')
                        
                        # Filter out non-English products
                        if not NutritionService.is_english_text(product_name):
                            continue
                        
                        nutrition = {
                            'name': product_name,
                            'brands': product.get('brands', ''),
                            'calories': float(product.get('energy-kcal_100g', 0) or 0),
                            'protein': float(product.get('proteins_100g', 0) or 0),
                            'carbs': float(product.get('carbohydrates_100g', 0) or 0),
                            'fat': float(product.get('fat_100g', 0) or 0),
                            'code': product.get('code', '')
                        }
                        products.append(nutrition)
                
                if products:
                    # Check if any products have actual nutrition data
                    has_nutrition = any(
                        p.get('calories', 0) > 0 or 
                        p.get('protein', 0) > 0 or 
                        p.get('carbs', 0) > 0 or 
                        p.get('fat', 0) > 0 
                        for p in products
                    )
                    if has_nutrition:
                        return {'products': products}
                    # Products returned but no nutrition data, skip to fallback
                    print(f"Products found but no nutrition data for: {query}")
                    break
                    
            except requests.RequestException as e:
                print(f"Error with endpoint {endpoint['url']}: {e}")
                continue
            except (KeyError, TypeError, ValueError) as e:
                print(f"Error parsing results from {endpoint['url']}: {e}")
                continue
        
        # Fallback to local database if API fails
        print(f"API search failed, trying fallback database for: {query}")
        fallback_results = NutritionService.search_fallback_database(query, limit)
        if fallback_results:
            return {'products': fallback_results}
        
        # If all methods fail, return empty results
        print(f"No results found for query: {query}")
        return {'products': []}
    
    @staticmethod
    def extract_nutrition_data(product_data: Dict) -> Dict:
        """
        Extract nutrition values from product data.
        Values are per 100g unless otherwise specified.
        
        Args:
            product_data: Product data from Open Food Facts API
            
        Returns:
            Dictionary with nutrition values
        """
        if not product_data:
            return {
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0,
                'product_name': '',
                'brands': '',
                'code': ''
            }
        
        # Handle both direct product data and nested structure
        if 'product' in product_data:
            product_data = product_data['product']
        
        nutrition = {
            'calories': float(product_data.get('energy-kcal_100g', 0) or 0),
            'protein': float(product_data.get('proteins_100g', 0) or 0),
            'carbs': float(product_data.get('carbohydrates_100g', 0) or 0),
            'fat': float(product_data.get('fat_100g', 0) or 0),
            'product_name': product_data.get('product_name', ''),
            'brands': product_data.get('brands', ''),
            'code': product_data.get('code', '')
        }
        
        return nutrition
    
    @staticmethod
    def get_cached_nutrition(barcode: str) -> Optional[Dict]:
        """
        Get nutrition data from cache if available.
        
        Args:
            barcode: Product barcode
            
        Returns:
            Cached nutrition data or None
        """
        cache_key = f"nutrition_{barcode}"
        return cache.get(cache_key)
    
    @staticmethod
    def cache_nutrition(barcode: str, nutrition_data: Dict):
        """
        Cache nutrition data for a product.
        
        Args:
            barcode: Product barcode
            nutrition_data: Nutrition data to cache
        """
        cache_key = f"nutrition_{barcode}"
        cache.set(cache_key, nutrition_data, NutritionService.CACHE_TIMEOUT)
    
    @staticmethod
    def get_nutrition_with_cache(barcode: str) -> Dict:
        """
        Get nutrition data with caching support.
        
        Args:
            barcode: Product barcode
            
        Returns:
            Nutrition data dictionary
        """
        # Try cache first
        cached_data = NutritionService.get_cached_nutrition(barcode)
        if cached_data:
            return cached_data
        
        # Fetch from API
        result = NutritionService.search_by_barcode(barcode)
        nutrition = NutritionService.extract_nutrition_data(result)
        
        # Cache the result
        if nutrition.get('code'):
            NutritionService.cache_nutrition(barcode, nutrition)
        
        return nutrition