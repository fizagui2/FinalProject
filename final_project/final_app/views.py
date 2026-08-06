from django.shortcuts import render

def home(request):
    return render(request, 'home.html', {})

def login_view(request):
    return render(request, 'login.html')

def feed(request):
    return render(request, 'categories.html')

def community(request):
    return render(request, 'forums.html')

def news(request):
    return render(request, 'news.html')

def shop(request):
    return render(request, 'shop.html')