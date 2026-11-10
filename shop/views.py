from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import Product, Order, OrderItem
from .forms import RegisterForm, CheckoutForm


def home(request):

    products = Product.objects.all()

    return render(request, "shop/home.html", {
        "products": products
    })


def product_detail(request, id):

    product = get_object_or_404(Product, id=id)

    return render(request, "shop/product.html", {
        "product": product
    })


def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()
            login(request, user)

            return redirect("home")

    else:
        form = RegisterForm()

    return render(request, "shop/register.html", {
        "form": form
    })


def login_page(request):

    from django.contrib.auth import authenticate

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:

            login(request, user)
            return redirect("home")

        messages.error(request, "Invalid username or password")

    return render(request, "shop/login.html")


def cart(request):

    return render(request, "shop/cart.html", {
        "cart": request.session.get("cart", {})
    })


def add_to_cart(request, id):

    if request.method == "POST":

        product = get_object_or_404(Product, id=id)

        if product.stock <= 0:
            messages.error(request, "Product out of stock")
            return redirect("home")

        cart = request.session.get("cart", {})

        key = str(id)

        quantity = int(cart.get(key, 0))

        if quantity < product.stock:
            cart[key] = quantity + 1

        request.session["cart"] = cart

    return redirect("cart")


def remove_from_cart(request, id):

    if request.method == "POST":

        cart = request.session.get("cart", {})

        cart.pop(str(id), None)

        request.session["cart"] = cart

    return redirect("cart")


@login_required
def checkout(request):

    cart = request.session.get("cart", {})

    if not cart:
        return redirect("home")

    products = Product.objects.filter(
        id__in=cart.keys()
    )

    total = sum(
        product.price * int(cart[str(product.id)])
        for product in products
    )

    if request.method == "POST":

        form = CheckoutForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                # Check stock again before creating the order.
                for product in products:
                    product.refresh_from_db()

                    quantity = int(cart[str(product.id)])

                    if product.stock < quantity:
                        messages.error(
                            request,
                            f"Insufficient stock for {product.name}"
                        )
                        return redirect("cart")

                order = Order.objects.create(
                    user=request.user,
                    full_name=form.cleaned_data["full_name"],
                    address=form.cleaned_data["address"],
                    total=total
                )

                for product in products:

                    quantity = int(cart[str(product.id)])

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price
                    )

                    product.stock -= quantity
                    product.save()

            request.session["cart"] = {}

            return render(request, "shop/orders.html", {
                "order": order
            })

    else:
        form = CheckoutForm()

    return render(request, "shop/checkout.html", {
        "form": form,
        "total": total
    })


@login_required
def my_orders(request):

    orders = Order.objects.filter(user=request.user)

    return render(request, "shop/orders.html", {
        "orders": orders
    })