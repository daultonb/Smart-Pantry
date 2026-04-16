from django.urls import path
from . import views

urlpatterns = [
    # Inventory routes
    path('', views.pantry_dashboard, name='pantry_dashboard'),
    path('add/', views.add_item, name='add_item'),
    path('edit/<int:pk>/', views.edit_item, name='edit_item'),
    path('delete/<int:pk>/', views.delete_item, name='delete_item'),
    path('consume/<int:pk>/', views.consume_item, name='consume_item'),
    path('shopping-list/', views.shopping_list, name='shopping_list'),
    path('restock/<int:pk>/', views.restock_item, name='restock_item'),
    path('analytics/', views.analytics, name='analytics'),
    
    # Feature #2: Recipe routes
    path('recipes/', views.recipe_dashboard, name='recipe_dashboard'),
    path('recipes/add/', views.add_recipe, name='add_recipe'),
    path('recipes/edit/<int:pk>/', views.edit_recipe, name='edit_recipe'),
    path('recipes/delete/<int:pk>/', views.delete_recipe, name='delete_recipe'),
    path('recipes/cook/<int:pk>/', views.cook_recipe, name='cook_recipe'),
    
    # Nutrition API routes
    path('nutrition/search/', views.nutrition_search_by_name, name='nutrition_search_by_name'),
    path('nutrition/barcode/<barcode>/', views.nutrition_search_by_barcode, name='nutrition_search_by_barcode'),
]
