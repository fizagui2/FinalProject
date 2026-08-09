from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.GameHubLoginView.as_view(), name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('categories/', views.feed, name='categories'),
    path('forums/', views.community, name='forums'),
    path('forums/post/create/', views.create_post, name='create_post'),
    path('forums/post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('forums/post/<int:post_id>/vote/<str:direction>/', views.vote_post, name='vote_post'),
    path('news/', views.news, name='news'),
    path('shop/', views.shop, name='shop'),
]