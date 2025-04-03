from django.urls import path
from .views import  category_list_create, category_detail, product_list_create, product_detail,customer_dashboard,admin_dashboard,register_user,login_user
urlpatterns = [
    # path('users/', user_list, name='user-list'),
    # path('users/<str:username>/', user_detail, name='user-detail'),
    path('auth/register/', register_user, name='register-user'),
    path('auth/login/', login_user, name='login-user'),
    path('dashboard/customer/', customer_dashboard, name='customer-dashboard'),
    path('dashboard/admin/', admin_dashboard, name='admin-dashboard'),
    path('categories/', category_list_create, name='category-list-create'),
    path('categories/<str:category_id>/', category_detail, name='category-detail'),

    # Product URLs
    path('products/', product_list_create, name='product-list-create'),
    path('products/<str:product_id>/', product_detail, name='product-detail'),
    
]
