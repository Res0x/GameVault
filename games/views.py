from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponseNotAllowed
from django.urls import reverse
from .models import Game
from django.db.models import Q


def home(request):
    games = Game.objects.all()
    total_games = games.count()
    playing_games = games.filter(status=Game.Status.PLAYING).count()
    completed_games = games.filter(status=Game.Status.COMPLETED).count()
    planned_games = games.filter(status=Game.Status.PLANNED).count()

    featured_game = (games
                     .filter(rating__isnull=False)
                     .order_by('-rating', '-release_year', 'title')
                     .first())

    context = {
        'page_title': 'GameVault',
        'subtitle': 'Личная библиотека видеоигр',
        'description': (
            'Здесь можно хранить игры, которые ты проходишь, '
            'уже прошел или только планируешь пройти.'
        ),
        'total_games': total_games,
        'playing_games': playing_games,
        'completed_games': completed_games,
        'planned_games': planned_games,
        'featured_game': featured_game,
    }

    return render(request, 'games/home.html', context)


def game_list(request):
    search_query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    games = Game.objects.all()
    statuses = Game.Status.values

    if status not in statuses:
        status = ''

    if search_query:
        games = games.filter(Q(title__icontains=search_query) |
                             Q(genre__icontains=search_query))
    if status:
        games = games.filter(status=status)

    context = {
        'page_title': 'Список игр',
        'games': games,
        'games_count': games.count(),
        'q': search_query,
        'selected_status': status,
    }

    return render(request, 'games/game_list.html', context)


def ratings(request):
    rated_games = [
        {
            'title': 'The Witcher 3',
            'genre': 'RPG',
            'status': 'Пройдено',
            'rating': 10,
        },
        {
            'title': 'Cyberpunk 2077',
            'genre': 'RPG',
            'status': 'Прохожу',
            'rating': 9,
        },
        {
            'title': 'Hades',
            'genre': 'Roguelike',
            'status': 'Пройдено',
            'rating': 9,
        },
        {
            'title': 'Disco Elysium',
            'genre': 'RPG',
            'status': 'Пройдено',
            'rating': 8,
        },
        {
            'title': 'Control',
            'genre': 'Action',
            'status': 'Пройдено',
            'rating': 8,
        },
    ]

    context = {
        'page_title': 'Рейтинг игр',
        'rated_games': rated_games,
    }

    return render(request, 'games/ratings.html', context)


def game_create(request):
    if request.method not in ('GET', 'POST'):
        return HttpResponseNotAllowed(['GET', 'POST'])
    submitted_game = None

    errors = {}

    form_data = {
        'title': '',
        'genre': '',
        'platform': '',
        'status': '',
        'play_mode': '',
        'features': [],
        'rating': '',
        'description': '',
    }

    platform_labels = {
        'pc': 'PC',
        'playstation': 'PlayStation',
        'xbox': 'Xbox',
        'switch': 'Nintendo Switch',
    }

    status_labels = {
        'planned': 'Хочу пройти',
        'playing': 'Прохожу',
        'completed': 'Пройдено',
    }

    play_mode_labels = {
        'single': 'Одиночная игра',
        'multiplayer': 'Мультиплеер',
        'both': 'Одиночная игра и мультиплеер',
    }

    feature_labels = {
        'story': 'Сюжетная игра',
        'open_world': 'Открытый мир',
        'coop': 'Кооператив',
    }

    if request.method == 'POST':
        platform = request.POST.get('platform', '')
        status = request.POST.get('status', '')
        play_mode = request.POST.get('play_mode', '')
        selected_features = request.POST.getlist('features')
        title = request.POST.get('title', '')
        genre = request.POST.get('genre', '')
        rating = request.POST.get('rating', '')
        description = request.POST.get('description', '')

        form_data = {
            'title': title,
            'genre': genre,
            'platform': platform,
            'status': status,
            'play_mode': play_mode,
            'features': selected_features,
            'rating': rating,
            'description': description,
        }

        platform = platform.strip()
        status = status.strip()
        title = title.strip()
        genre = genre.strip()
        rating = rating.strip()
        description = description.strip()

        feature_names = [
            feature_labels[feature]
            for feature in selected_features
            if feature in feature_labels
        ]
        if not title:
            errors['title'] = 'Введите название игры.'

        if not genre:
            errors['genre'] = 'Введите жанр игры.'

        if platform not in platform_labels:
            errors['platform'] = 'Выберите допустимую платформу.'

        if status not in status_labels:
            errors['status'] = 'Выберите допустимый статус.'

        if not errors:
            submitted_game = {
                'title': title,
                'genre': genre,
                'platform_display': platform_labels.get(platform, ''),
                'status_display': status_labels.get(status, ''),
                'play_mode_display': play_mode_labels.get(play_mode, ''),
                'features_display': (
                    ', '.join(feature_names)
                    if feature_names
                    else 'Не выбраны'
                ),
                'rating': rating,
                'description': description,
            }

    context = {
        'page_title': 'Добавить игру',
        'submitted_game': submitted_game,
        'errors': errors,
        'form_data': form_data,
    }

    return render(request, 'games/game_create.html', context)


def game_detail(request, game_slug):
    game = get_object_or_404(Game, slug=game_slug)
    recommendations = Game.objects.exclude(pk=game.pk)[:2]

    context = {
        'page_title': game.title,
        'game': game,
        'recommendations': recommendations,
    }

    return render(request, 'games/game_detail.html', context)


def games_by_year(request, release_year):
    games = Game.objects.all()
    games = games.filter(release_year=release_year).order_by('title')
    if not games.exists():
        raise Http404(f'Игры за {release_year} год не найдены')

    context = {
        'page_title': f'Игры за {release_year} год',
        'release_year': release_year,
        'games': games,
        'games_amount': games.count(),
    }

    return render(request, 'games/games_by_year.html', context)

def latest_game(request):
    games = Game.objects.all()
    games = games.order_by('-release_year', 'title')
    newest_game = games.first()
    if not newest_game:
        raise Http404('Игры еще не добавлены')


    latest_game_page = reverse(
        'games:game_detail',
        kwargs={'game_slug': newest_game.slug},
    )

    return redirect(latest_game_page)