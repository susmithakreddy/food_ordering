from django.urls import path
from . import views
from .views import restaurant_list, restaurant_detail, order_summary, checkout,order_confirmation

urlpatterns = [
   path('', views.restaurant_list, name='restaurant_list'),
    path('profile/', views.user_profile, name='user_profile'),
    path('accounts/login/', views.login_view, name='account_login'),
    path('accounts/signup/', views.signup_view, name='account_signup'),
    path('accounts/logout/', views.logout_view, name='account_logout'),
    path('restaurant/<int:id>/', views.restaurant_detail, name='restaurant_detail'),
    path('webhook/', views.webhook, name='stripe-webhook'),
    path('checkout/<int:order_id>/', checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', order_confirmation, name='order_confirmation'),
    path('order-summary/<int:order_id>/', order_summary, name='order_summary'),
]
