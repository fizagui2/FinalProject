from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.urls import reverse

from django.db import transaction

from .forms import SignUpForm
from .models import (Category, Post, Comment, Vote, Product, Cart, CartItem, Order, OrderItem, )

from .forms import SignUpForm
from .models import Category, Post, Comment, Vote


def home(request):
    return render(request, 'home.html', {})


class GameHubLoginView(LoginView):
    """Renders the shared login/register page and authenticates the login form."""

    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # The template shows Login and Register as tabs on one page, so the
        # login view still needs an (empty) register form to render the tab.
        context['register_form'] = SignUpForm()
        context['active_tab'] = 'login'
        return context


def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # log the new user straight in
            return redirect('home')
    else:
        form = SignUpForm()

    context = {
        'form': AuthenticationForm(),
        'register_form': form,
        'active_tab': 'register',
    }
    return render(request, 'login.html', context)


def feed(request):
    return render(request, 'categories.html')

def community(request):
    categories = Category.objects.all()

    posts = list(
        Post.objects
        .select_related('author', 'category')
        .prefetch_related('comments__author')
        .annotate(score=Coalesce(Sum('votes__value'), Value(0)))
        .order_by('-created_at')
    )

    #Look up how the current user voted on each post so that the template can highlight the right arrow
    user_votes = {}
    if request.user.is_authenticated:
        user_votes = dict(
            Vote.objects.filter(user=request.user, post__in=posts)
            .values_list('post_id', 'value')
        )
    for post in posts:
        post.user_vote = user_votes.get(post.id, 0)

    context = {
        'categories': categories,
        'posts': posts,
    }
    return render(request, 'forums.html', context)


@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        category = get_object_or_404(Category, pk=request.POST.get('category'))

        if title and body:
            Post.objects.create(author=request.user, category=category, title=title, body=body)
        else:
            messages.error(request, 'A post needs both a title and some content.')

    return redirect('forums')


@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        body = request.POST.get('body', '').strip()

        if body:
            Comment.objects.create(post=post, author=request.user, body=body)

    return redirect(f"{reverse('forums')}#post-{post_id}")


@login_required
def vote_post(request, post_id, direction):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        value = 1 if direction == 'up' else -1

        existing_vote = Vote.objects.filter(post=post, user=request.user).first()
        if existing_vote and existing_vote.value == value:
            existing_vote.delete()  # clicking the active arrow again clears the vote
        elif existing_vote:
            existing_vote.value = value
            existing_vote.save()
        else:
            Vote.objects.create(post=post, user=request.user, value=value)

    return redirect(f"{reverse('forums')}#post-{post_id}")

def news(request):
    return render(request, 'news.html')

# >> shop stuff
def shop(request):
    products = Product.objects.select_related('category').all()
    product_type = request.GET.get('type')
    category_id = request.GET.get('category')
    if product_type:
        products = products.filter(product_type=product_type)
    if category_id:
        products = products.filter(category_id=category_id)
    categories = Category.objects.all()
    context = {'products':products, 'categories':categories,}
    return render(request, 'shop.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('category'), slug=slug)
    return render(request, 'product_detail.html', {'product':product})

@login_required
def cart(request):
    user_cart, created = Cart.objects.get_or_create(user=request.user)
    items = user_cart.items.select_related('product')
    context = {'cart':user_cart,'items':items,}
    return render(request, 'cart.html', context)

@login_required
def add_to_cart(request, product_id):
    if request.method != 'POST':
        return redirect('shop')
    product = get_object_or_404(Product, id=product_id)
    if product.stock <= 0:
        messages.error(request, f'{product.name} is currently out of stock.')
    user_cart, created = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=user_cart, product=product)

    if created:
        item.quantity = 1
    else:
        if item.quantity < product.stock:
            item.quantity += 1
        else:
            messages.warning(request, 'You cannot add more than the available stock.')
            return redirect('cart')
    item.save()
    messages.success(request, f'{product.name} was added to your cart.')
    return redirect('cart')

@login_required
def update_cart(request, item_id):
    if request.method != 'POST':
        return redirect('cart')
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    if quantity <= 0:
        item.delete()
        return redirect('cart')
    if quantity > item.product.stock:
        messages.error(request, f'Only {item.product.stock} units are available.')
        return redirect('cart')
    item.quantity = quantity
    item.save()
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        item.delete()
    return redirect('cart')

@login_required
@transaction.atomic
def checkout(request):
    user_cart = get_object_or_404(Cart, user=request.user)
    items = list(user_cart.items.select_related('product'))
    if not items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')
    for item in items:
        if item.quantity > item.product.stock:
            messages.error(request, f'Not enough stock for {item.product.name}.')
            return redirect('cart')
    total = sum(item.product.price * item.quantity for item in items)
    order = Order.objects.create(user=request.user, total=total, status='pending')
    for item in items:
        OrderItem.objects.create(order=order, product=item.product, product_name=item.product.name, price=item.product.price, quantity=item.quantity,)
        item.product.stock -= item.quantity
        item.product.save(update_fields=['stock'])
    user_cart.items.all().delete()
    messages.success(request, f'Order #{order.id} created successfully.')
    return redirect('order_detail', order_id=order.id)

@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders':user_orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related('items'), id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order':order})

def aboutus(request):
    return render(request, 'aboutus.html')