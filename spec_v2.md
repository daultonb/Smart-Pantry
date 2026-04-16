# Specification: Smart Pantry Version 2 (Future Enhancements)

## Overview
Version 2 focuses on automation, advanced analytics, and quality-of-life improvements to reduce manual data entry.

## Planned Features

### 1. Nutritional API Integration
- **Feature:** Replace manual macro entry with an API (e.g., Nutritionix, Edamam).
- **Logic:** Search for the item name during consumption and pull standard nutritional data per portion.

### 2. Recipe Templates
- **Feature:** "One-Click" consumption for common meals.
- **Logic:** Create a `Recipe` model that links multiple `GroceryItems` and their required portions. Clicking "Cook Recipe" decrements all associated items simultaneously.

### 3. Financial Analytics
- **Feature:** Price tracking and pantry valuation.
- **Logic:** 
    - Calculate total current value of all food in the house.
    - Track price history of specific items to visualize inflation or find the cheapest store.

### 4. Advanced Inventory Logic
- **Feature:** Multi-unit support.
- **Logic:** Support for weight (grams/oz) in addition to portions for items like bulk grains or meat.

### 5. User Accounts & Cloud Sync
- **Feature:** User authentication.
- **Logic:** Move from local MongoDB to MongoDB Atlas to allow access from mobile devices while at the grocery store.

### 6. Waste Tracking
- **Feature:** "Discarded" log.
- **Logic:** Track items that were thrown away due to expiration to identify patterns of over-buying.