from django.urls import path
from .views import *
from . import views
from django.contrib.auth import views as auth_views
from django.urls import path

urlpatterns = [
    path('',index,name="index"),
    path('base/',base,name="base"),
    path('about/',about,name="about"),
    path('checkout/',checkout,name="checkout"),
    path('contact/',contact,name="contact"),
    path('shop_single/',shop_single,name="shop_single"),
    path('thankyou/',thankyou,name="thankyou"),
    path('login/',login, name="login"),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    path('pago/', pago, name='pago'),
    path('pago_transferencia/', pago_transferencia, name='pago_transferencia'),

    #URLs VENDEDOR
    path('home_vendedor/', home_vendedor, name="home_vendedor"),
    path('update_pedido/<str:id_pedido>/', update_pedido, name='update_pedido'),

    #URLs BODEGUERO
    path('home_bodeguero/', home_bodeguero, name="home_bodeguero"),
    path('update_pedido_bodeguero/<str:id_pedido>/', update_pedido_bodeguero, name='update_pedido_bodeguero'),

    #URLs CONTADOR
    path('home_contador/', home_contador, name="home_contador"),
    path('update_pago/<str:id_pago>/', update_pago, name='update_pago'),

    #Rutas del crud del admin
    path('home_admin/',home_admin, name="home_admin"),
    path('add_empleado/',add_empleado, name="add_empleado"),
    path('update_empleado/<str:rut>/', update_empleado, name='update_empleado'),
    path('delete_empleado/<str:rut>/', delete_empleado, name='delete_empleado'),

    #Rutas de la lógica del carrito
    path('shop/',productos_view,name="shop"),
    path('cart/',cart,name="cart"),
    path('carrito/agregar/', agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/', actualizar_carrito, name='actualizar_carrito'),
    #EMAIL
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),  name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    
    
]