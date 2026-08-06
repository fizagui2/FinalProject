from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('categories/', views.feed, name='categories'),
    path('forums/', views.community, name='forums'),
    path('news/', views.news, name='news'),
    path('shop/', views.shop, name='shop'),
]