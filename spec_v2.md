# Specification: Smart Pantry Version 2 (Future Enhancements)

## Overview
Version 2 focuses on automation, advanced analytics, and quality-of-life improvements to reduce manual data entry.

## Planned Features

### 1. Nutritional API Integration
- **Feature:** Replace manual macro entry with an API (e.g., Nutritionix, Edamam).
- **Logic:** Search for the item name during consumption and pull standard nutritional data per portion.
- **Implementation:** API key registration, Django service layer for HTTP requests, and "Auto-fill" button in `ConsumptionForm`.
- **Difficulty:** 3/5

### 2. Recipe Templates
- [x] **Feature:** "One-Click" consumption for common meals.
- [x] **Logic:** Create a `Recipe` model that links multiple `GroceryItems` and their required portions. Clicking "Cook Recipe" decrements all associated items simultaneously.
- [x] **Implementation:** `Recipe` and `RecipeIngredient` models, Recipe Dashboard, and atomic transaction view for simultaneous decrements.
- [x] **Difficulty:** 3/5

### 3. Financial Analytics
- [x] **Feature:** Price tracking and pantry valuation.
- [x] **Logic:** 
    - [x] Calculate total current value of all food in the house.
    - [x] Track price history of specific items to visualize inflation or find the cheapest store.
- [x] **Implementation:** Valuation aggregation logic, `PriceHistory` model for tracking, and Chart.js integration for visualization.
- [x] **Difficulty:** 2/5

### 4. Advanced Inventory Logic
- [x] **Feature:** Multi-unit support.
- [x] **Logic:** Support for weight (grams/oz) in addition to portions for items like bulk grains or meat.
- [x] **Implementation:** Refactor `GroceryItem` model to use `quantity` (Decimal) and `unit` fields; update all views to handle decimal math and unit conversions.
- [x] **Difficulty:** 4/5

### 5. User Accounts & Cloud Sync
- **Feature:** User authentication.
- **Logic:** Move from local SQLite to a cloud database to allow access from mobile devices while at the grocery store.
- **Implementation:** Django `User` authentication, adding `ForeignKey(User)` to items and logs, and migrating to a cloud DB (e.g., PostgreSQL/MongoDB Atlas).
- **Difficulty:** 3/5

### 6. Waste Tracking
- **Feature:** "Discarded" log.
- **Logic:** Track items that were thrown away due to expiration to identify patterns of over-buying.
- **Implementation:** "Discard" button on dashboard, `WasteLog` model, and a "Total Value Lost" analytics view.
- **Difficulty:** 1/5
