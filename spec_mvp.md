# Specification: Smart Pantry MVP (Version 1) - STATUS: COMPLETED

## Project Overview
A web application to track grocery inventory, automate shopping lists, and log nutritional intake. The system focuses on "portions" rather than weight to simplify tracking.

## Tech Stack
- **Backend:** Django (Python)
- **Database:** SQLite (Local for development)
- **Frontend:** Django Templates, HTML, CSS (Tailwind)

## Core Data Model
### GroceryItem
- `name` (String) [x]
- `category` (String/Enum) [x]
- `total_portions` (Integer) [x]
- `remaining_portions` (Integer) [x]
- `low_stock_threshold` (Integer) [x]
- `price` (Decimal) [x]
- `expiry_date` (Date) [x]

### ConsumptionLog
- `item` (Reference to GroceryItem) [x]
- `portions_consumed` (Integer) [x]
- `calories` (Float) [x]
- `protein` (Float) [x]
- `carbs` (Float) [x]
- `fat` (Float) [x]
- `timestamp` (DateTime) [x]

---

## Implementation Phases

### Phase 0: Skeleton & Environment
**Goal:** A running Django project connected to SQLite with a "Hello World" page.
- [x] Initialize Python virtual environment.
- [x] Install Django and SQLite.
- [x] Configure `settings.py` for SQLite connection.
- [x] Create a basic "Home" view and template.
- **Test Gap:** Server starts and displays the home page without DB errors.

### Phase 1: Inventory Management (CRUD)
**Goal:** Ability to add, view, and edit grocery items.
- [x] Implement `GroceryItem` model.
- [x] Create "Add Item" form with pre-filled default portions (editable).
- [x] Create "Pantry Dashboard" view listing all current items.
- [x] Implement "Edit" and "Delete" functionality.
- **Test Gap:** Can add a "Bag of Apples" with 6 portions and see it on the dashboard.

### Phase 2: Consumption & Macro Logging
**Goal:** Subtract portions and log the nutritional data at the time of use.
- [x] Create "Consume Item" interface (input for number of portions).
- [x] Implement macro input fields (Cal, Pro, Carb, Fat) during consumption.
- [x] Logic to decrement `remaining_portions` in `GroceryItem`.
- [x] Save entry to `ConsumptionLog`.
- **Test Gap:** Consuming 2 portions of chicken reduces inventory and creates a log entry with macros.

### Phase 3: Automated Shopping List
**Goal:** Automatic generation of a shopping list based on thresholds.
- [x] Implement logic: `Shopping List = Items where remaining_portions <= low_stock_threshold`.
- [x] Create "Shopping List" view.
- [x] Implement "Restock" action: Resets `remaining_portions` to `total_portions` and updates price/expiry.
- **Test Gap:** Item automatically appears on shopping list when portions drop to threshold; disappears after restocking.

### Phase 4: Final Polish & Local Testing
**Goal:** UX improvements and data validation.
- [x] Add basic CSS styling (Tailwind) for mobile responsiveness.
- [x] Add validation to prevent negative portions.
- [x] Implement "Expiring Soon" visual indicators (color coding).
- **Test Gap:** Full end-to-end flow from Purchase -> Consumption -> Shopping List -> Restock.