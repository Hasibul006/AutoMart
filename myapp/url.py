from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('profile', views.profile, name='profile'),
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('edit_user/<str:user_name>', views.edit_user, name='edit_user'),
    path('delete_user/<str:user_name>', views.delete_user, name='delete_user'),
    path('add_product', views.add_product, name='add_product'),
    path('update_product/<int:product_id>', views.update_product, name='update_product'),
    path('delete_product/<int:product_id>', views.delete_product, name='delete_product'),
    path('product_details/<int:product_id>', views.product_details, name='product_details'),
    path('add_category', views.add_category, name='add_category'),
    path('delete_category/<str:category_name>', views.delete_category, name='delete_category'),
    path('products', views.products, name='products'),
    path('search', views.search, name='search'),
    path('logout', views.logout, name='logout'),
    path('add_to_cart/<int:product_id>', views.add_to_cart, name='add_to_cart'),
    path('cart', views.cart, name='cart'),
    path('remove_from_cart/<int:product_id>', views.remove_from_cart, name='remove_from_cart'),
    path('add_to_cart_with_quantity/<int:product_id>', views.add_to_cart_with_quantity, name='add_to_cart_with_quantity'),
    path('update_cart_quantity/<int:product_id>', views.update_cart_quantity, name='update_cart_quantity'),
    path('checkout', views.checkout, name='checkout'),
    path('place_order', views.place_order, name='place_order'),
    path('orderDetails/<int:order_id>', views.orderDetails, name='orderDetails'),
]
