from django.urls import path
from . import views

app_name = 'stores'

urlpatterns = [
    # Marketplace
    path("", views.MarketplaceView.as_view(), name="marketplace"),

    # Categories
    path("categories/<slug:slug>/", views.StoreListView.as_view(), name="store_category"),
    path("products/category/<slug:slug>/", views.ProductListView.as_view(), name="product_category"),
    
    # Stores
    path("stores/", views.StoreListView.as_view(), name="stores"),
    path("store/<int:pk>/", views.StoreDetailView.as_view(), name="store_detail"),

    # Products
    path("products/", views.ProductListView.as_view(), name="products"),
    path("product/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("product/<int:product_id>/variant/", views.GetVariantView.as_view(), name="get_variant"),

    # Cart
    path("cart/", views.CartDetailView.as_view(), name="cart"),
    path("cart/add/<int:product_id>/", views.CartAddView.as_view(), name="cart_add"),
    path("cart/add/<int:product_id>/<int:variant_id>/", views.CartAddVariantView.as_view(), name="cart_add_variant"),
    path("cart/update/<int:item_id>/", views.CartUpdateView.as_view(), name="cart_update"),
    path("cart/remove/<int:item_id>/", views.CartRemoveView.as_view(), name="cart_remove"),

    # Checkout
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("checkout/address/", views.CheckoutAddressView.as_view(), name="checkout_address"),
    path("checkout/payment/", views.CheckoutPaymentView.as_view(), name="checkout_payment"),
    path("checkout/confirm/", views.OrderCreateView.as_view(), name="checkout_confirm"),

    # # Orders
    # path("orders/", views.OrderListView.as_view(), name="orders"),
    # path("order/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    # path("order/<int:pk>/cancel/", views.OrderCancelView.as_view(), name="order_cancel"),

    # # Customer Addresses
    # path("addresses/", views.AddressListView.as_view(), name="addresses"),
    # path("address/add/", views.AddressCreateView.as_view(), name="address_add"),
    # path("address/<int:pk>/edit/", views.AddressUpdateView.as_view(), name="address_edit"),
    # path("address/<int:pk>/delete/", views.AddressDeleteView.as_view(), name="address_delete"),

    # # Payment
    # path("payment/<int:order_id>/", views.PaymentView.as_view(), name="payment"),

    # # Seller / Store Orders
    # path("dashboard/orders/", views.StoreOrderListView.as_view(), name="store_orders"),
    # path("dashboard/order/<int:pk>/", views.StoreOrderDetailView.as_view(), name="store_order_detail"),
    # path("dashboard/order/<int:pk>/status/", views.StoreOrderStatusUpdateView.as_view(), name="store_order_status"),
]

