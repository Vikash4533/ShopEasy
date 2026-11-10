from django.urls import path
from . import views

urlpatterns = [

    path("", views.home, name="home"),

    path("product/<int:id>/",
         views.product_detail,
         name="product"),

    path("register/",
         views.register,
         name="register"),

    path("login/",
         views.login_page,
         name="login"),

    path("cart/",
         views.cart,
         name="cart"),

    path("add-cart/<int:id>/",
         views.add_to_cart,
         name="add_cart"),

    path("remove-cart/<int:id>/",
         views.remove_from_cart,
         name="remove_cart"),

    path("checkout/",
         views.checkout,
         name="checkout"),

    path("my-orders/",
         views.my_orders,
         name="my_orders"),

]