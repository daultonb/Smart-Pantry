from django.db import models

class GroceryItem(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    total_portions = models.IntegerField()
    remaining_portions = models.IntegerField()
    low_stock_threshold = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.remaining_portions}/{self.total_portions})"

class ConsumptionLog(models.Model):
    item = models.ForeignKey(GroceryItem, on_delete=models.CASCADE, related_name='consumption_logs')
    portions_consumed = models.IntegerField()
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} - {self.portions_consumed} portions on {self.timestamp}"
