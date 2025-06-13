from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'shop'

urlpatterns = [
    # Основные страницы
    path('', views.welcome, name='welcome'),
    path('about/', views.about, name='about'),
    path('catalog/', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Корзина
    path('cart/', views.cart_detail, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    
    # Заказы
    path('checkout/', views.checkout, name='checkout'),
    
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='shop/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    
    # Смена пароля
    path('password-change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='shop/password_change.html',
             success_url='password-change-done/'
         ),
         name='password_change'),
    path('password-change-done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='shop/password_change_done.html'
         ),
         name='password_change_done'),
    
    # Сброс пароля
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='shop/password_reset.html',
             email_template_name='shop/password_reset_email.html',
             subject_template_name='shop/password_reset_subject.txt'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='shop/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='shop/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='shop/password_reset_complete.html'
         ),
         name='password_reset_complete'),
] 