from django.urls import path
from . import views

urlpatterns = [
    path('', views.pantry_dashboard, name='pantry_dashboard'),
    path('add/', views.add_item, name='add_item'),
    path('edit/<int:pk>/', views.edit_item, name='edit_item'),
    path('delete/<int:pk>/', views.delete_item, name='delete_item'),
    path('consume/<int:pk>/', views.consume_item, name='consume_item'),
    path('shopping-list/', views.shopping_list, name='shopping_list'),
    path('restock/<int:pk>/', views.restock_item, name='restock_item'),
]
