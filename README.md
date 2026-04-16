# 🥗 Smart Pantry

[![Django](https://img.shields.io/badge/Django-4.2-blue.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Smart Pantry** is a comprehensive food inventory management system that helps you track groceries, manage recipes, monitor nutrition, and optimize your pantry expenses. Built with Django, it combines practical inventory tracking with powerful analytics and Open Food Facts integration.

---

## 📋 Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### 🏠 Core Inventory Management
- **Multi-Unit Support**: Track items in portions, grams, kilograms, ounces, pounds, milliliters, liters, cups, tablespoons, teaspoons, or pieces
- **Expiry Date Tracking**: Never let food go to waste with visual indicators for expired and near-expiry items
- **Low Stock Alerts**: Automatic detection of items running low with customizable thresholds
- **Price Tracking**: Monitor price changes across different stores with historical data
- **Smart Restocking**: One-click restocking that resets items to their original quantities

### 📖 Recipe Management
- **Recipe Templates**: Create and save custom recipes with multiple ingredients
- **Ingredient Tracking**: Link recipes to your inventory items with precise amounts
- **Cook Mode**: Atomically consume all ingredients when cooking a recipe
- **Missing Ingredients Detection**: See what you're missing before you start cooking
- **Recipe Instructions**: Store step-by-step cooking instructions

### 🥗 Nutrition Integration (Open Food Facts)
- **Barcode Lookup**: Scan product barcodes to automatically fetch nutrition data
- **Name Search**: Search for products by name with intelligent suggestions
- **Nutrition Logging**: Track calories, protein, carbs, and fat consumption
- **Caching System**: Fast lookups with intelligent caching for frequently accessed products
- **English-First Search**: Optimized for English product names with fallback support

### 📊 Financial Analytics
- **Pantry Valuation**: Real-time calculation of your pantry's total monetary value
- **Category Breakdown**: Visual charts showing value distribution by food category
- **Store Comparison**: Compare spending across different stores
- **Price History**: Track price trends over time for individual items
- **Time Range Analysis**: Analyze data over 7, 14, 30, or 60-day periods

### 🎨 User Experience
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Bootstrap 5 UI**: Modern, clean interface with intuitive navigation
- **AJAX Search**: Real-time product search without page reloads
- **Visual Indicators**: Color-coded status badges for item conditions
- **Progress Bars**: Visual quantity tracking for each item

---

## 🖼️ Screenshots

### Dashboard
![Dashboard](SmartPantryV1/dashboard.png)
*Main inventory dashboard with expiry tracking and quick actions*

### Recipe Management
![Recipes](SmartPantryV2/recipe_dashboard.png)
*Create and manage custom recipes with ingredient tracking*

### Analytics
![Analytics](SmartPantryV2/analytics.png)
*Financial insights with interactive charts*

### Nutrition Search
![Nutrition](SmartPantryV2/nutrition_search.png)
*Open Food Facts integration for nutrition data*

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **Backend Framework** | Django 4.2 |
| **Language** | Python 3.10+ |
| **Database** | SQLite (default) / PostgreSQL (production) |
| **Frontend** | Bootstrap 5, HTML5, CSS3 |
| **JavaScript** | Vanilla JS, Chart.js |
| **API Integration** | Open Food Facts API |
| **Testing** | pytest, Django Test Framework |
| **Browser Testing** | Playwright |

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smart-pantry.git
   cd smart-pantry
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env and add your settings
   # OPEN_FOOD_FACTS_API_URL=https://world.openfoodfacts.org
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Load sample data (optional)**
   ```bash
   python seed_pantry.py
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   Open your browser and navigate to `http://localhost:8000`

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key for security | Required |
| `DEBUG` | Debug mode (True/False) | True |
| `OPEN_FOOD_FACTS_API_URL` | Open Food Facts API endpoint | https://world.openfoodfacts.org |
| `NUTRITION_CACHE_TTL` | Nutrition cache time-to-live (seconds) | 86400 (24 hours) |

### Database Configuration

For production deployments, update `smart_pantry/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'smart_pantry',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 📖 Usage

### Adding Items

1. Navigate to the Dashboard
2. Click "Add Item"
3. Fill in the item details:
   - Name, Category, Price
   - Quantity and Unit (grams, cups, portions, etc.)
   - Expiry Date, Store
4. Click "Save"

### Using Nutrition Search

1. When adding or consuming items, click "Search Nutrition"
2. Enter a product name or barcode
3. Select from search results to auto-fill nutrition data
4. The system caches results for faster future lookups

### Creating Recipes

1. Go to "Recipes" in the navigation
2. Click "Add Recipe"
3. Enter recipe name, description, and instructions
4. Add ingredients by selecting from your inventory
5. Specify required amounts for each ingredient
6. Save the recipe

### Cooking a Recipe

1. Find your recipe in the Recipe Dashboard
2. Click "Cook" on the recipe card
3. Review ingredients and check availability
4. If all ingredients are available, confirm to cook
5. All ingredients are consumed atomically

### Viewing Analytics

1. Navigate to "Analytics"
2. Select time range (7, 14, 30, or 60 days)
3. View interactive charts:
   - Pantry value over time
   - Value by category (pie chart)
   - Value by store (bar chart)
   - Price history trends

---

## 🔌 API Endpoints

### Nutrition Search

#### Search by Name
```http
GET /api/nutrition/search/?q=<query>
```

**Response:**
```json
{
  "products": [
    {
      "code": "001234567890",
      "name": "Organic Whole Milk",
      "brands": "Brand Name",
      "calories": 60,
      "protein": 3.4,
      "carbs": 5.0,
      "fat": 3.3
    }
  ]
}
```

#### Search by Barcode
```http
GET /api/nutrition/barcode/<barcode>/
```

**Response:**
```json
{
  "code": "001234567890",
  "name": "Organic Whole Milk",
  "brands": "Brand Name",
  "calories": 60,
  "protein": 3.4,
  "carbs": 5.0,
  "fat": 3.3
}
```

---

## 📁 Project Structure

```
smart-pantry/
├── smart_pantry/              # Main project configuration
│   ├── settings.py           # Django settings
│   ├── urls.py              # URL routing
│   └── views.py             # Home page views
├── inventory/                 # Core application
│   ├── models.py            # Data models (GroceryItem, Recipe, etc.)
│   ├── views.py             # View functions
│   ├── forms.py             # Django forms
│   ├── urls.py              # App URL routing
│   └── services/            # Business logic
│       └── nutrition_service.py  # Open Food Facts integration
├── templates/                 # HTML templates
│   ├── base.html            # Base template
│   ├── home.html            # Home page
│   └── inventory/           # Inventory templates
│       ├── dashboard.html
│       ├── recipe_form.html
│       ├── analytics.html
│       └── ...
├── tests/                     # Test suite
│   ├── test_nutrition_search.py
│   └── test_nutrition_english.py
├── manage.py                 # Django management script
├── seed_pantry.py            # Sample data generator
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

---

## 🧪 Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test tests.test_nutrition_search

# Run with coverage
pytest --cov=inventory
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

---

## 📊 Data Models

### GroceryItem
```python
- name: str
- category: str
- quantity: Decimal (remaining)
- total_quantity: Decimal (original)
- unit: str (portion, grams, cups, etc.)
- price: Decimal
- expiry_date: Date
- store: str
```

### Recipe
```python
- name: str
- description: str
- instructions: str
- ingredients: [RecipeIngredient]
```

### RecipeIngredient
```python
- recipe: ForeignKey(Recipe)
- item: ForeignKey(GroceryItem)
- required_amount: Decimal
```

### ConsumptionLog
```python
- item: ForeignKey(GroceryItem)
- portions_consumed: int
- calories: float
- protein: float
- carbs: float
- fat: float
- timestamp: DateTime
```

---

## 🔐 Security Considerations

- Never commit `.env` files with sensitive data
- Use strong `SECRET_KEY` in production
- Enable HTTPS for production deployments
- Keep Django and dependencies updated
- Use database user with minimal privileges

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Open Food Facts](https://world.openfoodfacts.org/) for the nutrition data API
- [Django](https://www.djangoproject.com/) for the web framework
- [Bootstrap](https://getbootstrap.com/) for the UI framework
- [Chart.js](https://www.chartjs.org/) for data visualization

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: support@smartpantry.example.com

---

**Built with ❤️ by Smart Pantry Team**

*Track smarter. Waste less. Eat better.*