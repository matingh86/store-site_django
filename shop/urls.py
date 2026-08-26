from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from shop.models import Order
from . import views


app_name="shop"
urlpatterns=[
    path("",views.home,name="home"),
    path("register",views.registerview.as_view(),name="register"),
    path("login",views.loginview.as_view(),name="login"),
    path("logout",views.logoutview.as_view(),name="logout"),
    path("product_list",views.productlist.as_view(),name="product_list"),
    path("product_detail/<slug:slug>",views.productdetail.as_view(),name="product_detail"),
    path("search",views.search.as_view(),name="search"),
    path("phone_otp",views.sendotp.as_view(),name="sendotp"),
    path("otp_check",views.checkotp.as_view(),name="checkotp"),
    path('cart_detail/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart_detail/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart_detail', views.cart_detail, name='cart_detail'),
    path('order_create', views.order_create, name='order_create'),
    path('order_detail/<int:order_id>', views.order_detail, name='order_detail'),
    path('process/<int:order_id>/', views.payment_process, name='payment_process'),
    path('verify/', views.payment_verify, name='payment_verify'),
    path('coupon/apply/', views.copounview, name='coupon_apply'),

    path('about_us', views.about_us, name="about_us"),
    path('call_us', views.ticket, name="call_us"),
    path('faq/', views.faq, name='faq'),
    path('profile', views.profile, name='profile'),
    path('edit_profile', views.update_prfile, name='update_profile'),
    path('category/<str:category_slug>/', views.productlist.as_view(), name='product_list_by_category'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# جابه‌جا کردن صفحه اصلی ادمین با تابع جدید

