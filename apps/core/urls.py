from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Expense URLs
    path('expenses/', views.ExpenseListView.as_view(), name='expense_list'),
    path('expenses/create/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('expenses/<int:pk>/', views.ExpenseDetailView.as_view(), name='expense_detail'),
    path('expenses/<int:pk>/update/', views.ExpenseUpdateView.as_view(), name='expense_update'),
    path('expenses/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense_delete'),
    
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Card URLs
    path('cards/', views.CardListView.as_view(), name='card_list'),
    path('cards/sync/', views.CardSyncListView.as_view(), name='card_sync_list'),
    path('cards/<int:pk>/sync-action/', views.sync_card_action, name='card_sync_action'),
    path('cards/create/', views.CardCreateView.as_view(), name='card_create'),
    path('cards/<int:pk>/update/', views.CardUpdateView.as_view(), name='card_update'),
    path('cards/<int:pk>/delete/', views.CardDeleteView.as_view(), name='card_delete'),
] 