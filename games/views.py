from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponseNotAllowed
from django.urls import reverse
from .models import Game, Feature
from django.db.models import Q, Avg, Count, Min, Max
from .forms import GameForm

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
    games = Game.objects.prefetch_related('features')
    statuses = Game.Status.values

    if status not in statuses:
        status = ''

    if search_query:
        normalized_query = search_query.casefold()

        matching_feature_ids = [
            feature.pk
            for feature in Feature.objects.only('pk', 'name')
            if normalized_query in feature.name.casefold()
        ]

        games = games.filter(
            Q(title__icontains=search_query)
            | Q(genre__icontains=search_query)
            | Q(features__pk__in=matching_feature_ids)
        ).distinct()
    if status:
        games = games.filter(status=status)

    context = {
        'page_title': 'Список игр',
        'games': games,
        'games_count': len(games),
        'q': search_query,
        'selected_status': status,
    }

    return render(request, 'games/game_list.html', context)


def ratings(request):
    rated_base = Game.objects.filter(
        rating__isnull=False,
    )

    rating_summary = rated_base.aggregate(
        total_rated=Count('id'),
        average_rating=Avg('rating'),
        highest_rating=Max('rating'),
        lowest_rating=Min('rating'),
    )

    rated_games = (
        rated_base
        .annotate(
            features_count=Count(
                'features',
                distinct=True,
            ),
        )
        .order_by(
            '-rating',
            '-release_year',
            'title',
        )
    )

    genre_stats = (
        rated_base
        .values('genre')
        .annotate(
            games_count=Count('id'),
            average_rating=Avg('rating'),
            highest_rating=Max('rating'),
        )
        .order_by(
            '-average_rating',
            'genre',
        )
    )

    context = {
        'page_title': 'Рейтинг игр',
        'rated_games': rated_games,
        'rating_summary': rating_summary,
        'genre_stats': genre_stats,
    }

    return render(request, 'games/ratings.html', context)


def game_create(request):
    if request.method not in ('GET', 'POST'):
        return HttpResponseNotAllowed(['GET', 'POST'])

    elif request.method == 'POST':
        form = GameForm(request.POST)
        if form.is_valid():
            game = form.save()
            game_page = reverse(
                'games:game_detail',
                kwargs={'game_slug': game.slug}
            )
            return redirect(game_page)
    else:
        form = GameForm()
    context = {
        'page_title': 'Добавить игру',
        'form_heading': 'Данные об игре',
        'form_description': 'Заполни основные сведения об игре.',
        'submit_text': 'Добавить игру',
        'form': form,
    }

    return render(request, 'games/game_form.html', context)


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

def game_edit(request, game_slug):
    if request.method not in ('GET', 'POST'):
        return HttpResponseNotAllowed(['GET', 'POST'])

    game = get_object_or_404(Game, slug=game_slug)
    if request.method == 'GET':
        form = GameForm(instance=game)
    else:
        form = GameForm(request.POST, instance=game)
        if form.is_valid():
            updated_game = form.save()
            updated_game_page = reverse(
                'games:game_detail',
                kwargs={'game_slug': updated_game.slug},
            )
            return redirect(updated_game_page)
    context = {
        'page_title': f'Редактирование {game.title}',
        'form_heading': 'Изменение данных',
        'form_description': 'Измени сведения об игре и сохрани результат.',
        'submit_text': 'Сохранить изменения',
        'form': form,
    }
    return render(request, 'games/game_form.html', context)