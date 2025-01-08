from django.urls import path
from .views import admin, products, cart, checkout

urlpatterns = [
    # Vistas públicas y productos
    path('', products.index, name='index'),
    path('products/', products.product_list, name='product_list'),
    path('product/<slug:slug>/', products.product_detail, name='product_detail'),
    path('category/<slug:slug>/', products.category_products, name='category_products'),
    path('brand/<slug:slug>/', products.brand_products, name='brand_products'),
    path('products/add-review/<int:product_id>/', products.add_review, name='add_review'),

    # Carrito de compras
    path('cart/', cart.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', cart.cart_add, name='cart_add'),
    path('cart/update/', cart.cart_update, name='cart_update'),
    path('cart/remove/<int:product_id>/', cart.cart_remove, name='cart_remove'),
    path('cart/apply-coupon/', cart.apply_coupon, name='apply_coupon'),
    path('cart/remove-coupon/', cart.remove_coupon, name='remove_coupon'),

    # Proceso de checkout
    path('checkout/', checkout.checkout, name='checkout'),
    path('order/success/<int:order_id>/', checkout.order_success, name='order_success'),


    # Panel de administración
    path('dashboard/', admin.admin_dashboard, name='admin_dashboard'),
    # Gestión de productos
    path('dashboard/products/', admin.product_list_admin, name='product_list_admin'),
    path('dashboard/products/create/', admin.product_create, name='product_create'),
    path('dashboard/products/<int:pk>/edit/', admin.product_edit, name='product_edit'),
    path('dashboard/products/<int:pk>/delete/', admin.product_delete, name='product_delete'),

    # Gestión de pedidos
    path('dashboard/orders/', admin.order_list_admin, name='order_list_admin'),
    path('dashboard/orders/<int:order_id>/', admin.order_detail_admin, name='order_detail_admin'),

]