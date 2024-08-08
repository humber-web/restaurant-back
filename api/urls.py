# api/urls.py
from django.contrib import admin
from django.urls import path
from core.Views.user_views import CreateUserView, ProfileView, GroupListView, UserListView, UserDetailView, UserUpdateView, UserDeleteView
from core.Views.auth_views import CreateCustomerView, LoginView
from core.Views.menu_category_views import CreateMenuCategoryView, MenuCategoryListView, MenuCategoryDetailView, MenuCategoryUpdateView, MenuCategoryDeleteView
from core.Views.menu_item_views import CreateMenuItemView, MenuItemListView, MenuItemDetailView, MenuItemUpdateView, MenuItemDeleteView
from core.Views.inventory_item_views import CreateInventoryItemView, InventoryItemListView, InventoryItemDetailView, InventoryItemUpdateView, InventoryItemDeleteView
from core.Views.table_views import CreateTableView, TableListView, TableDetailView, TableUpdateView, TableDeleteView
from core.Views.order_views import CreateOrderView, UpdateOrderItemsView, TransferOrderItemsView, ListOrdersView, OrderDetailView, DeleteOrderView
from core.Views.payment_views import ProcessPaymentView
from core.Views.insert_extract_money_views import InsertMoneyView, ExtractMoneyView
from core.Views.cash_register_views import StartCashRegisterView,CloseCashRegisterView

urlpatterns = [
    # Users url
    path('admin/', admin.site.urls),
    path('api/register/', CreateUserView.as_view(), name='register'),
    path('api/register/customer/', CreateCustomerView.as_view(), name='register_customer'),
    path('api/user/', UserListView.as_view(), name='users'),
    path('api/user/<int:pk>/', UserDetailView.as_view(), name='user'),
    path('api/user/<int:pk>/update/', UserUpdateView.as_view(), name='update_user'),
    path('api/user/<int:pk>/delete/', UserDeleteView.as_view(), name='delete_user'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/profile/', ProfileView.as_view(), name='profiles'),
    path('api/group/', GroupListView.as_view(), name='groups'),
    
    
    # MenuCategory url
    path('api/menu_category/register', CreateMenuCategoryView.as_view(), name='menu_category_register'),
    path('api/menu_category/', MenuCategoryListView.as_view(), name='menu_categories'),
    path('api/menu_category/<int:pk>/', MenuCategoryDetailView.as_view(), name='menu_category'),
    path('api/menu_category/<int:pk>/update/', MenuCategoryUpdateView.as_view(), name='update_menu_category'),
    path('api/menu_category/<int:pk>/delete/', MenuCategoryDeleteView.as_view(), name='delete_menu_category'),
    
    
    # MenuItem url
    path('api/menu_item/register', CreateMenuItemView.as_view(), name='menu_item_register'),
    path('api/menu_item/', MenuItemListView.as_view(), name='menu_items'),
    path('api/menu_item/<int:pk>/', MenuItemDetailView.as_view(), name='menu_item'),
    path('api/menu_item/<int:pk>/update/', MenuItemUpdateView.as_view(), name='update_menu_item'),
    path('api/menu_item/<int:pk>/delete/', MenuItemDeleteView.as_view(), name='delete_menu_item'),
    path('api/menu_item/search/', MenuItemDetailView.as_view(), name='search_menu_item'),
    
    
    # InventoryItem url
    path('api/inventory_item/register', CreateInventoryItemView.as_view(), name='inventory_item_register'),
    path('api/inventory_item/',InventoryItemListView.as_view(), name='inventory_items'),
    path('api/inventory_item/<int:pk>/',InventoryItemDetailView.as_view(),name='inventory_item'),
    path('api/inventory_item/<int:pk>/update/', InventoryItemUpdateView.as_view(), name='update_inventory_item'),
    path('api/inventory_item/<int:pk>/delete/', InventoryItemDeleteView.as_view(), name='delete_inventory_item'),
    path('api/inventory_item/search/', InventoryItemDetailView.as_view(), name='search_inventory_item'),
    
    
    # Table url
    path('api/table/register', CreateTableView.as_view(), name='table_register'),
    path('api/table/', TableListView.as_view(), name='tables'),
    path('api/table/<int:pk>/', TableDetailView.as_view(), name='table'),
    path('api/table/search/', TableDetailView.as_view(), name='search_table'),
    path('api/table/<int:pk>/update/', TableUpdateView.as_view(), name='update_table'),
    path('api/table/<int:pk>/delete/', TableDeleteView.as_view(), name='delete_table'),
    
    
    # Order url
    path('api/order/register', CreateOrderView.as_view(), name='order_register'),
    path('api/order/', ListOrdersView.as_view(), name='orders'),
    path('api/order/<int:pk>/update/', UpdateOrderItemsView.as_view(), name='update-order'),
    path('api/order/transfer/', TransferOrderItemsView.as_view(), name='transfer-order-items'),
    path('api/order/<int:pk>/', OrderDetailView.as_view(), name='order'),
    path('api/order/search/', OrderDetailView.as_view(), name='search_order'),
    path('api/order/<int:pk>/delete/', DeleteOrderView.as_view(), name='delete_order'),
    
    
    
    path('api/payment/register/', ProcessPaymentView.as_view(), name='payment_register'),
    # path('api/payment/<int:payment_id>/update/', UpdatePaymentStatusView.as_view(), name='update_payment_status'),
    
    
    
    # Insert and Extract Money url
    path('api/cash_register/insert_money/', InsertMoneyView.as_view(), name='insert-money'),
    path('api/cash_register/start/', StartCashRegisterView.as_view(), name='start-cash-register'),
    path('api/cash_register/extract_money/', ExtractMoneyView.as_view(), name='extract-money'),
    path('api/cash_register/close/', CloseCashRegisterView.as_view(), name='close-cash-register'),
    
    
    
    
]
