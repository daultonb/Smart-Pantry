"""
Playwright test for nutrition search functionality.
Tests the Open Food Facts API integration for auto-filling nutrition data.
"""
from playwright.sync_api import sync_playwright, expect
import time

def test_nutrition_search():
    """Test that nutrition search works and auto-fills nutrition fields."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to the dashboard
        page.goto("http://127.0.0.1:8000/inventory/", timeout=30000)
        
        # Wait for page to load
        page.wait_for_selector("h2", state="visible")
        
        # Find the first grocery item and click consume
        consume_button = page.locator("a:has-text('Consume')").first
        consume_button.click()
        
        # Wait for the consume page to load
        page.wait_for_url(lambda url: "consume" in str(url), timeout=10000)
        
        # Check that product name is auto-populated
        product_name_input = page.locator("input.product-search-input")
        expect(product_name_input).to_be_visible()
        
        # Get the auto-populated value
        product_name = product_name_input.input_value()
        print(f"Auto-populated product name: {product_name}")
        
        # Wait for auto-search to complete (give it more time for network request)
        time.sleep(3)
        
        # Check if nutrition fields were auto-filled (if single match found)
        calories = page.locator('input[name="calories"]').input_value()
        protein = page.locator('input[name="protein"]').input_value()
        carbs = page.locator('input[name="carbs"]').input_value()
        fat = page.locator('input[name="fat"]').input_value()
        
        print(f"Auto-filled nutrition data - Calories: {calories}, Protein: {protein}, Carbs: {carbs}, Fat: {fat}")
        
        # Verify auto-fill worked
        if calories or protein or carbs or fat:
            print("✓ Auto-fill worked correctly")
        else:
            print("✗ Auto-fill did not work")
        
        # Check if suggestions appeared (may or may not depending on API response)
        suggestions = page.locator("#product-suggestions")
        
        # Try to search for a common food item
        product_name_input.fill("chicken breast")
        time.sleep(1)  # Wait for debounce
        
        # Check if suggestions appeared
        suggestion_items = page.locator(".suggestion-item")
        count = suggestion_items.count()
        print(f"Found {count} suggestions for 'chicken breast'")
        
        # If suggestions exist, click the first one
        if count > 0:
            suggestion_items.first.click()
            time.sleep(0.5)
            
            # Check if nutrition fields were filled
            calories = page.locator('input[name="calories"]').input_value()
            protein = page.locator('input[name="protein"]').input_value()
            carbs = page.locator('input[name="carbs"]').input_value()
            fat = page.locator('input[name="fat"]').input_value()
            
            print(f"Nutrition data - Calories: {calories}, Protein: {protein}, Carbs: {carbs}, Fat: {fat}")
            
            # Verify at least some nutrition data was filled
            assert calories or protein or carbs or fat, "No nutrition data was filled"
        
        # Test the nutrition search API endpoint directly
        response = page.goto("http://127.0.0.1:8000/inventory/nutrition/search/?q=chicken")
        print(f"API Response status: {response.status}")
        
        browser.close()
        
        print("✓ Nutrition search test completed")

if __name__ == "__main__":
    test_nutrition_search()