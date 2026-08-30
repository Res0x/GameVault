from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView
from django.db.models import Q, Count, Avg, Max, Min
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from games.models import Game
from library.forms import LibraryEntryForm
from library.mixins import UserEntriesMixin
from library.models import LibraryEntry


class LibraryEntryListView(LoginRequiredMixin, UserEntriesMixin ,ListView):
    model = LibraryEntry
    template_name = 'library/library_list.html'
    context_object_name = 'entries'
    paginate_by = 9

    def get_queryset(self):
        entries = super().get_queryset().with_game_features()
        self.search_query = self.request.GET.get('q', '').strip()
        self.status = self.request.GET.get('status', '').strip()

        if self.status not in LibraryEntry.Status.values:
            self.status = ''

        if self.search_query:

            entries = entries.filter(
                Q(game__title__icontains=self.search_query) |
                Q(game__genre__icontains=self.search_query) |
                Q(game__developer__icontains=self.search_query)
            )

        if self.status:
            entries = entries.filter(status=self.status)

        return entries

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Моя библиотека'
        context['entries_count'] = context['paginator'].count
        context['q'] = self.search_query
        context['selected_status'] = self.status
        context['status_choices'] = LibraryEntry.Status.choices

        request_copy = self.request.GET.copy()
        request_copy.pop('page', None)
        request_copy = request_copy.urlencode()
        if request_copy:
            request_copy = '&' + request_copy
        context['query_string'] = request_copy

        return context

@login_required
@require_POST
def library_entry_add(request, game_slug):
    game = get_object_or_404(Game, slug=game_slug)

    entry, created = LibraryEntry.objects.get_or_create(
        user=request.user,
        game=game,
    )

    if created:
        messages.success(request, 'Игра успешно добавлена в библиотеку!')
    else:
        messages.info(request, 'Игра уже есть в вашей библиотеке!')

    return redirect('games:game_detail',game_slug=game.slug)

class LibraryEntryUpdateView(LoginRequiredMixin, UserEntriesMixin, UpdateView):
    model = LibraryEntry
    form_class = LibraryEntryForm
    template_name = 'library/library_entry_form.html'
    context_object_name = 'entry'
    success_url = reverse_lazy('library:library_list')

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(self.request, 'Данные успешно обновлены!')

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Редактирование записи'
        return context

class LibraryEntryDeleteView(LoginRequiredMixin, UserEntriesMixin, DeleteView):
    model = LibraryEntry
    template_name = 'library/library_entry_confirm_delete.html'
    success_url = reverse_lazy('library:library_list')

    def form_valid(self, form):
        game_title = self.object.game.title
        response = super().form_valid(form)

        messages.success(self.request, f'{game_title} удалена из вашей библиотеки.')

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Удаление игры {self.object.game.title}'
        context['game_title'] = self.object.game.title
        return context

@login_required
def ratings(request):
    rated_base = LibraryEntry.objects.for_user(request.user).with_game().rated()

    rating_summary = rated_base.aggregate(
        total_rated=Count('id'),
        average_rating=Avg('rating'),
        highest_rating=Max('rating'),
        lowest_rating=Min('rating'),
    )

    rated_entries = (
        rated_base
        .annotate(
            features_count=Count(
                'game__features',
                distinct=True,
            ),
        )
        .order_by(
            '-rating',
            '-game__release_year',
            'game__title',
        )
    )

    genre_stats = (
        rated_base
        .values('game__genre')
        .annotate(
            games_count=Count('id'),
            average_rating=Avg('rating'),
            highest_rating=Max('rating'),
        )
        .order_by(
            '-average_rating',
            'game__genre',
        )
    )

    context = {
        'page_title': 'Рейтинг игр',
        'rated_entries': rated_entries,
        'rating_summary': rating_summary,
        'genre_stats': genre_stats,
    }

    return render(request, 'library/ratings.html', context)
