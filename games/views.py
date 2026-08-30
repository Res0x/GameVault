from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponseNotAllowed
from django.urls import reverse, reverse_lazy
from django.db.models import Q, ProtectedError
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib import messages

from .forms import GameForm, GameAuthenticationForm, GameUserCreationForm, GamePasswordChangeForm, \
    GamePasswordResetForm, GameSetPasswordForm, GameUserUpdateForm
from .models import Game
from library.models import LibraryEntry

def home(request):

    games = Game.objects.all()
    total_games = games.count()
    completed_games = None
    planned_games = None
    playing_games = None
    featured_game = None
    total_entries = None


    if request.user.is_authenticated:
        entries = LibraryEntry.objects.for_user(request.user).with_game()
        total_entries = entries.count()
        playing_games = entries.filter(status=LibraryEntry.Status.PLAYING).count()
        completed_games = entries.filter(status=LibraryEntry.Status.COMPLETED).count()
        planned_games = entries.filter(status=LibraryEntry.Status.PLANNED).count()
        featured_game = (entries
                     .rated()
                     .order_by('-rating', '-game__release_year', 'game__title')
                     .first())

    context = {
        'page_title': 'GameVault',
        'subtitle': 'Личная библиотека видеоигр',
        'description': (
            'Здесь можно хранить игры, которые ты проходишь, '
            'уже прошел или только планируешь пройти.'
        ),
        'total_games': total_games,
        'total_entries': total_entries,
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

        if self.search_query:
            games = games.filter(
                Q(title__icontains=self.search_query)
                | Q(genre__icontains=self.search_query)
                | Q(features__name__icontains=self.search_query)
            ).distinct()

        return games

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Список игр'
        context['games_count'] = context['paginator'].count
        context['q'] = self.search_query

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
        context['library_entry'] = None

        if self.request.user.is_authenticated:
            context['library_entry'] = (
                self.object.library_entries
                .for_user(self.request.user)
                .first()
            )
        context['page_title'] = self.object.title
        context['recommendations'] = Game.objects.exclude(pk=self.object.pk)[:2]
        return context

class GameCreateView(PermissionRequiredMixin, CreateView):
    model = Game
    form_class = GameForm
    template_name = 'games/game_form.html'
    permission_required = 'games.add_game'

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)

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


class GameUpdateView(PermissionRequiredMixin, UpdateView):
    model = Game
    form_class = GameForm
    template_name = 'games/game_form.html'
    slug_url_kwarg = 'game_slug'
    permission_required = 'games.change_game'

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

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.has_perm('games.manage_all_games'):
            return queryset

        return queryset.filter(
            added_by=self.request.user
        )

class GameDeleteView(PermissionRequiredMixin, DeleteView):
    model = Game
    template_name = 'games/game_confirm_delete.html'
    slug_url_kwarg = 'game_slug'
    success_url = reverse_lazy('games:game_list')
    permission_required = 'games.delete_game'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Удаление игры {self.object.title}'
        context['has_user_data'] = bool(self.object.library_entries.count() + self.object.reviews.count())
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.has_perm('games.manage_all_games'):
            return queryset

        return queryset.filter(
            added_by=self.request.user
        )

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, 'Нельзя удалить игру, с которой связаны пользовательские данные!')
            url = reverse('games:game_detail', kwargs={'game_slug': self.object.slug})
            return redirect(url)


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

class GameRegisterView(CreateView):
    form_class = GameUserCreationForm
    template_name = 'games/register.html'
    success_url = reverse_lazy('games:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Регистрация'
        return context

class GamePasswordChangeView(PasswordChangeView):
    form_class = GamePasswordChangeForm
    template_name = 'games/password_change.html'
    success_url = reverse_lazy('games:change_password_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Смена пароля'
        return context

class GamePasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'games/password_change_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Пароль изменен'
        return context

class GamePasswordResetView(PasswordResetView):
    form_class = GamePasswordResetForm
    template_name = 'games/password_reset.html'
    email_template_name = 'games/password_reset_email.txt'
    subject_template_name = 'games/password_reset_subject.txt'
    success_url = reverse_lazy('games:password_reset_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Восстановление пароля'
        return context

class GamePasswordResetDoneView(PasswordResetDoneView):
    template_name = 'games/password_reset_done.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Сброс пароля выполнен'
        return context

class GamePasswordResetConfirmView(PasswordResetConfirmView):
    form_class = GameSetPasswordForm
    template_name = 'games/password_reset_confirm.html'
    success_url = reverse_lazy('games:password_reset_complete')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Восстановление пароля'
        return context

class GamePasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'games/password_reset_complete.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Пароль обновлен успешно!'
        return context

class GameProfileView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = 'games/profile.html'
    context_object_name = 'profile_user'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Профиль GameVault'
        return context

class GameProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = GameUserUpdateForm
    template_name = 'games/profile_edit.html'
    success_url = reverse_lazy('games:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Редактирование профиля GameVault'
        return context