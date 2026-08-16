from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.urls import reverse

from .forms import SignUpForm
from .models import Category, Post, Comment, Vote, User


def home(request):
    return render(request, 'home.html', {})


class GameHubLoginView(LoginView):
    """Renders the shared login/register page and authenticates the login form."""

    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

    #Look up how the current user voted on each post so that the template can highlight the arrow
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
        'member_count': User.objects.count(),
        'post_count': Post.objects.count(),
        'category_count': categories.count(),
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
            existing_vote.delete()  # clicking the arrow again clears out the votse
        elif existing_vote:
            existing_vote.value = value
            existing_vote.save()
        else:
            Vote.objects.create(post=post, user=request.user, value=value)

    return redirect(f"{reverse('forums')}#post-{post_id}")

def news(request):
    news_categories = [
        {'slug': 'playstation', 'name': 'PlayStation'},
        {'slug': 'xbox', 'name': 'Xbox'},
        {'slug': 'nintendo', 'name': 'Nintendo'},
        {'slug': 'pokemon', 'name': 'Pokémon'},
        {'slug': 'pc-gaming', 'name': 'PC Gaming'},
        {'slug': 'esports', 'name': 'Esports'},
    ]

    # Short list for the "Popular News" sidebar next to the featured story
    popular_news = [
        {'title': 'Mafia: Definitive Edition may be getting a native PS5 version', 'icon': 'bi-playstation'},
        {'title': "Xbox's Asha Sharma visits Bethesda for a live Elder Scrolls 6 playthrough", 'icon': 'bi-xbox'},
        {'title': 'GTA 6 finally has a release date: August 27', 'icon': 'bi-controller'},
        {'title': 'Pokémon Pokopia passes 5 million copies sold', 'icon': 'bi-lightning-charge'},
        {'title': 'Helldivers 2 joins PS Plus Extra and Premium this month', 'icon': 'bi-playstation'},
    ]

    # Stories for the "Trending News" row
    trending_articles = [
        {
            'title': 'Rocket League returns to the Esports World Cup with a $1M prize pool',
            'excerpt': 'Sixteen of the best Rocket League teams in the world are competing in Paris, August 12–16.',
            'image': 'images/news/rocketleague.jpg',
            'category': 'Esports',
            'icon': 'bi-trophy',
        },
        {
            'title': 'Esports World Cup 2026 kicks off its $2M CrossFire tournament',
            'excerpt': 'One of the largest prize pools of the summer as EWC 2026 rolls on in Paris.',
            'image': 'images/news/ewc.webp',
            'category': 'Esports',
            'icon': 'bi-trophy',
        },
        {
            'title': 'Gamescom 2026 is just a few weeks away',
            'excerpt': "Europe's biggest gaming showcase is expected to bring a fresh wave of reveals and trailers.",
            'image': 'images/news/gamescom.jpg',
            'category': 'PC Gaming',
            'icon': 'bi-globe',
        },
    ]

    featured_article = {
        'title': 'GTA 6 finally has a trailer release date: August 27',
        'excerpt': 'After years of speculation, Rockstar has locked in a new trailer date for Grand Theft Auto VI.',
        'body': "Rockstar Games has confirmed Grand Theft Auto VI is releasing a new trailer on August 27, closing the book on "
                "years of delays and speculation. It's shaping up to be the biggest release of the year across "
                'every platform, and easily one of the most anticipated games in the series’ history.',
        'category': 'PC Gaming',
        'category_slug': 'pc-gaming',
        'tags': ['#GTA6', '#ROCKSTAR', '#OPENWORLD'],
        'image': 'images/news/gta6n.jpg',
        'source': 'GameSpot',
        'date': 'Releases August 27',
        'icon': 'bi-controller',
    }

    articles = [
        {
            'title': 'Helldivers 2 joins PS Plus Extra and Premium this month',
            'excerpt': "Sony's hit co-op shooter is now included with a PS Plus Extra or Premium subscription.",
            'body': 'Helldivers 2 has been added to the PS Plus Extra and Premium game catalog for August 2026, '
                    "giving subscribers free access to Arrowhead's cooperative shooter without buying it outright. "
                    "It's one of the bigger additions to this month's PS Plus lineup.",
            'category': 'PlayStation',
            'category_slug': 'playstation',
            'tag': '#PSPLUS',
            'image': 'images/news/hd2.jpg',
            'source': 'Push Square',
            'date': 'This month',
            'icon': 'bi-playstation',
            'views': 12100,
            'trend_rank': 2,
        },
        {
            'title': 'Warner Bros. confirms the next Hogwarts Legacy is in development',
            'excerpt': 'Warner Bros. has officially acknowledged work has begun on a sequel to Hogwarts Legacy.',
            'body': 'Warner Bros. Games has confirmed that development is underway on the next entry in the '
                    'Hogwarts Legacy series, following years of fan requests for a sequel to the 2023 open-world hit. '
                    'No release window has been shared yet.',
            'category': 'PlayStation',
            'category_slug': 'playstation',
            'tag': '#HOGWARTSLEGACY',
            'image': 'images/news/hl2.png',
            'source': 'VGC',
            'date': 'This week',
            'icon': 'bi-playstation',
            'views': 9600,
            'trend_rank': 4,
        },
        {
            'title': 'Pokémon Pokopia passes 5 million copies sold',
            'excerpt': '21% of Switch 2 owners now own Pokémon Pokopia since its release back in March.',
            'body': 'The Pokémon Company and Game Freak confirmed Pokémon Pokopia has sold more than 5 million '
                    'copies since launching in March, with roughly 21% of all Nintendo Switch 2 owners now owning '
                    "a copy — a strong showing for one of the console's early exclusives.",
            'category': 'Pokémon',
            'category_slug': 'pokemon',
            'tag': '#POKOPIA',
            'image': 'images/news/pokemon.png',
            'source': 'Nintendo Life',
            'date': 'This week',
            'icon': 'bi-lightning-charge',
            'views': 15300,
            'trend_rank': 1,
        },
        {
            'title': 'Splatoon 3 announces a free crossover DLC',
            'excerpt': 'A new free crossover update is on the way for Splatoon 3, Nintendo confirms.',
            'body': 'Nintendo has announced a free crossover DLC coming to Splatoon 3, adding new content to the '
                    'ink-based shooter at no extra cost to owners. Details on the crossover partner are still '
                    'under wraps.',
            'category': 'Nintendo',
            'category_slug': 'nintendo',
            'tag': '#SPLATOON3',
            'image': 'images/news/splatoon.jpg',
            'source': 'GameRant',
            'date': 'This week',
            'icon': 'bi-nintendo-switch',
            'views': 7100,
            'trend_rank': 6,
        },
        {
            'title': "Xbox Game Pass's August departures list is smaller than usual",
            'excerpt': 'This wave of Game Pass removals is notably lighter than the last four months.',
            'body': "The first wave of Xbox Game Pass departures for August 2026 is smaller than it's been in "
                    'recent months, though it still includes a handful of notable titles leaving the service. '
                    'Microsoft has not commented on whether this signals a broader slowdown in rotation.',
            'category': 'Xbox',
            'category_slug': 'xbox',
            'tag': '#GAMEPASS',
            'image': 'images/news/xbox.jpg',
            'source': 'GameSpot',
            'date': 'This week',
            'icon': 'bi-xbox',
            'views': 6800,
            'trend_rank': 5,
        },
        {
            'title': 'Marvel Tōkon: Fighting Souls launches with 20 heroes and villains',
            'excerpt': 'Arc System Works ships its new Marvel fighting game with a full campaign and online battles.',
            'body': 'Arc System Works released Marvel Tōkon: Fighting Souls on August 6, featuring 20 playable '
                    'heroes and villains at launch, a single-player campaign, and both local and online versus '
                    'battles.',
            'category': 'PC Gaming',
            'category_slug': 'pc-gaming',
            'tag': '#MARVELTOKON',
            'image': 'images/news/marvel.jpg',
            'source': 'PC Gamer',
            'date': 'Launched August 6',
            'icon': 'bi-controller',
            'views': 8900,
            'trend_rank': 3,
        },
        {
            'title': 'Star Wars Zero Company blends XCOM tactics with the Force',
            'excerpt': 'Former XCOM developers at Bit Reactor bring turn-based tactics to a galaxy far, far away.',
            'body': 'Star Wars Zero Company, from former XCOM developers at Bit Reactor, releases August 27. It '
                    'mixes turn-based tactical combat and permadeath with a Star Wars setting that reportedly '
                    'features a young Anakin Skywalker.',
            'category': 'PC Gaming',
            'category_slug': 'pc-gaming',
            'tag': '#ZEROCOMPANY',
            'image': 'images/news/starwars.jpg',
            'source': 'GamesRadar',
            'date': 'Releases August 27',
            'icon': 'bi-controller',
            'views': 5400,
            'trend_rank': 7,
        },
        {
            'title': 'Metal Gear Solid 4 returns in Metal Gear Solid Collection Vol. 2',
            'excerpt': 'MGS4 is being re-released for the first time since the PS3 era, alongside Peace Walker.',
            'body': 'Konami confirmed Metal Gear Solid 4: Guns of the Patriots is being re-released as part of '
                    "Metal Gear Solid Collection Volume 2, bundled with Metal Gear Solid: Peace Walker — MGS4's "
                    'first re-release since it launched exclusively on PlayStation 3.',
            'category': 'PC Gaming',
            'category_slug': 'pc-gaming',
            'tag': '#METALGEARSOLID',
            'image': 'images/news/mgs4.jpg',
            'source': 'IGN',
            'date': 'This week',
            'icon': 'bi-disc',
            'views': 4700,
            'trend_rank': 8,
        },
    ]

    context = {
        'news_categories': news_categories,
        'featured_article': featured_article,
        'popular_news': popular_news,
        'trending_articles': trending_articles,
        'articles': articles,
    }
    return render(request, 'news.html', context)

def shop(request):
    return render(request, 'shop.html')