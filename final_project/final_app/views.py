from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.urls import reverse

from .models import Category, Post, Comment, Vote


def home(request):
    return render(request, 'home.html', {})

def login_view(request):
    return render(request, 'login.html')

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

def shop(request):
    return render(request, 'shop.html')