from django.db import models, transaction
from django.utils import timezone
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

# Unit choices for multi-unit support
UNIT_CHOICES = [
    ('portion', 'Portion'),
    ('grams', 'Grams (g)'),
    ('kilograms', 'Kilograms (kg)'),
    ('ounces', 'Ounces (oz)'),
    ('pounds', 'Pounds (lbs)'),
    ('milliliters', 'Milliliters (ml)'),
    ('liters', 'Liters (L)'),
    ('cups', 'Cups'),
    ('tablespoons', 'Tablespoons (tbsp)'),
    ('teaspoons', 'Teaspoons (tsp)'),
    ('pieces', 'Pieces'),
]

class GroceryItem(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    
    # Multi-unit support fields (Feature #4)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'))
    total_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'))
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='portion')
    
    # Legacy portion fields for backward compatibility (will be deprecated)
    total_portions = models.IntegerField(default=1, help_text="Legacy field - use total_quantity instead")
    remaining_portions = models.IntegerField(default=1, help_text="Legacy field - use quantity instead")
    low_stock_threshold = models.IntegerField(default=1)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()
    store = models.CharField(max_length=100, default='Unknown')

    def __str__(self):
        return f"{self.name} ({self.get_quantity_display()})"

    def get_quantity_display(self):
        """Display quantity with unit."""
        return f"{self.quantity} {self.unit}"

    def get_total_quantity_display(self):
        """Display total quantity with unit."""
        return f"{self.total_quantity} {self.unit}"

    def current_value(self):
        """Calculate proportional value based on remaining quantity."""
        if self.total_quantity > 0:
            return (self.quantity / self.total_quantity) * self.price
        return self.price * self.quantity

    @property
    def is_expired(self):
        """Check if item is expired."""
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

    @property
    def is_near_expiry(self):
        """Check if item is expiring within 3 days."""
        if self.expiry_date and not self.is_expired:
            return (self.expiry_date - timezone.now().date()).days <= 3
        return False

    @property
    def is_low_stock(self):
        """Check if item is low on stock."""
        return self.quantity <= self.low_stock_threshold
    
    def get_quantity_percentage(self):
        """Calculate the percentage of quantity remaining."""
        if self.total_quantity > 0:
            return float((self.quantity / self.total_quantity) * 100)
        return 0.0

    def can_consume(self, amount):
        """Check if item has enough quantity to consume."""
        return self.quantity >= amount

    def consume(self, amount):
        """Consume a specific amount of this item."""
        if not self.can_consume(amount):
            raise ValueError(f"Not enough {self.unit} left! Only {self.quantity} remaining.")
        self.quantity = self.quantity - amount
        self.save()
        return True

    def save(self, *args, **kwargs):
        """Track price history when price changes."""
        is_new = self.pk is None
        old_price = None
        old_store = None
        
        if not is_new:
            try:
                old_item = GroceryItem.objects.get(pk=self.pk)
                old_price = old_item.price
                old_store = old_item.store
            except GroceryItem.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Record price history if price or store changed
        if not is_new and (old_price != self.price or old_store != self.store):
            PriceHistory.objects.create(
                item=self,
                old_price=old_price if old_price else self.price,
                new_price=self.price,
                store=self.store,
                timestamp=timezone.now()
            )

# Feature #2: Recipe Templates
class Recipe(models.Model):
    """A recipe that can consume multiple grocery items at once."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    # Type hint for reverse relation (helps IDE type checking)
    if TYPE_CHECKING:
        ingredients: RelatedManager["RecipeIngredient"]

    def get_ingredients_count(self):
        """Return the number of ingredients in this recipe."""
        return self.ingredients.count()

    def can_cook(self):
        """Check if all ingredients have sufficient quantity."""
        for ingredient in self.ingredients.all():
            if not ingredient.item.can_consume(ingredient.required_amount):
                return False
        return True

    def get_missing_ingredients(self):
        """Return a list of ingredients that are insufficient."""
        missing = []
        for ingredient in self.ingredients.all():
            if not ingredient.item.can_consume(ingredient.required_amount):
                missing.append({
                    'item': ingredient.item,
                    'required': ingredient.required_amount,
                    'available': ingredient.item.quantity
                })
        return missing

    def cook(self):
        """
        Cook the recipe - atomically consume all ingredients.
        Returns a tuple of (success, message).
        """
        # First check if we can cook
        if not self.can_cook():
            missing = self.get_missing_ingredients()
            missing_names = [m['item'].name for m in missing]
            return False, f"Missing ingredients: {', '.join(missing_names)}"
        
        try:
            with transaction.atomic():
                # Consume all ingredients atomically
                for ingredient in self.ingredients.all():
                    ingredient.item.consume(ingredient.required_amount)
                return True, "Recipe cooked successfully!"
        except Exception as e:
            return False, f"Error cooking recipe: {str(e)}"

    class Meta:
        ordering = ['name']


class RecipeIngredient(models.Model):
    """Links a recipe to a grocery item with the required amount."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    item = models.ForeignKey(GroceryItem, on_delete=models.CASCADE, related_name='recipes')
    required_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.required_amount} {self.item.unit} of {self.item.name}"

    class Meta:
        ordering = ['item__name']
        unique_together = ['recipe', 'item']

class ConsumptionLog(models.Model):
    item = models.ForeignKey(GroceryItem, on_delete=models.CASCADE, related_name='consumption_logs')
    portions_consumed = models.IntegerField()
    calories = models.FloatField(default=0.0, null=True, blank=True)
    protein = models.FloatField(default=0.0, null=True, blank=True)
    carbs = models.FloatField(default=0.0, null=True, blank=True)
    fat = models.FloatField(default=0.0, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} - {self.portions_consumed} portions on {self.timestamp}"

class PriceHistory(models.Model):
    """Tracks price changes for grocery items."""
    item = models.ForeignKey(GroceryItem, on_delete=models.CASCADE, related_name='price_history')
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    store = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name}: ${self.old_price} -> ${self.new_price} at {self.store}"

    class Meta:
        ordering = ['-timestamp']