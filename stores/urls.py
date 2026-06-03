from django.urls import path
from . import views

app_name = 'stores'

urlpatterns = [
    path('', views.MarketplaceView.as_view(), name='marketplace'),

    path('products/', views.ProductListView.as_view(), name='products'),
    path('product-<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),

    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    # path('order/success/<int:order_id>/', views.order_confirmation, name='order_confirmation'),

    path('stores/', views.StoreListView.as_view(), name='stores'),
    path('store-<int:pk>/', views.StoreDetailView.as_view(), name='store_detail'),

    path('categories/<slug:slug>/', views.StoreListView.as_view(), name='store_category'),
    path('products/categories/<slug:slug>/', views.ProductListView.as_view(), name='product_category'),
    
    path('cart/', views.StoreListView.as_view(), name='cart'),
]

