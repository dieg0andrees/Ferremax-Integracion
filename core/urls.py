from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('',index,name="index"),
    path('base/',base,name="base"),
    path('about/',about,name="about"),
    path('cart/',cart,name="cart"),
    path('checkout/',checkout,name="checkout"),
    path('contact/',contact,name="contact"),
    path('shop_single/',shop_single,name="shop_single"),
    path('shop/',shop,name="shop"),
    path('thankyou/',thankyou,name="thankyou"),
    path('login/',login, name="login"),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register')
]