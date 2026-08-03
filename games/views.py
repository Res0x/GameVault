from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponseNotAllowed
from django.urls import reverse, reverse_lazy
from django.db.models import Q, Avg, Count, Min, Max
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import GameForm, GameAuthenticationForm
from .models import Game, Feature

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


class GameListView(ListView):
    model = Game
    template_name = 'games/game_list.html'
    context_object_name = 'games'
    paginate_by = 9

    def get_queryset(self):
        games = super().get_queryset()
        games = games.prefetch_related('features')
        self.search_query = self.request.GET.get('q', '').strip()
        self.status = self.request.GET.get('status', '').strip()

        if self.status not in Game.Status.values:
            self.status = ''

        if self.search_query:
            normalized_query = self.search_query.casefold()

            matching_feature_ids = [
                feature.pk
                for feature in Feature.objects.only('pk', 'name')
                if normalized_query in feature.name.casefold()
            ]

            games = games.filter(
                Q(title__icontains=self.search_query)
                | Q(genre__icontains=self.search_query)
                | Q(features__pk__in=matching_feature_ids)
            ).distinct()

        if self.status:
            games = games.filter(status=self.status)
        return games

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Список игр'
        context['games_count'] = context['paginator'].count
        context['q'] = self.search_query
        context['selected_status'] = self.status

        request_copy = self.request.GET.copy()
        request_copy.pop('page', None)
        request_copy = request_copy.urlencode()
        if request_copy:
            request_copy = '&' + request_copy
        context['query_string'] = request_copy

        return context


class GameDetailView(DetailView):
    model = Game
    template_name = 'games/game_detail.html'
    context_object_name = 'game'
    slug_url_kwarg = 'game_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.object.title
        context['recommendations'] = Game.objects.exclude(pk=self.object.pk)[:2]
        return context


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


class GameCreateView(LoginRequiredMixin, CreateView):
    model = Game
    form_class = GameForm
    template_name = 'games/game_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Добавить игру'
        context['form_heading'] = 'Данные об игре'
        context['form_description'] = 'Заполни основные сведения об игре.'
        context['submit_text'] = 'Добавить игру'
        return context

    def get_success_url(self):
        return reverse(
                'games:game_detail',
                kwargs={'game_slug': self.object.slug},
        )


class GameUpdateView(LoginRequiredMixin, UpdateView):
    model = Game
    form_class = GameForm
    template_name = 'games/game_form.html'
    slug_url_kwarg = 'game_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Редактирование {self.object.title}'
        context['form_heading'] = 'Изменение данных'
        context['form_description'] = 'Измени сведения об игре и сохрани результат.'
        context['submit_text'] = 'Сохранить изменения'
        return context

    def get_success_url(self):
        return reverse(
            'games:game_detail',
            kwargs={'game_slug': self.object.slug},
        )


class GameDeleteView(LoginRequiredMixin, DeleteView):
    model = Game
    template_name = 'games/game_confirm_delete.html'
    slug_url_kwarg = 'game_slug'
    success_url = reverse_lazy('games:game_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Удаление игры {self.object.title}'
        return context


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

class GameLoginView(LoginView):
    template_name = 'games/login.html'
    authentication_form = GameAuthenticationForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Вход'
        return context
