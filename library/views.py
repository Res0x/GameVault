from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from games.models import Game
from library.models import LibraryEntry


class LibraryEntryListView(LoginRequiredMixin, ListView):
    model = LibraryEntry
    template_name = 'library/library_list.html'
    context_object_name = 'entries'
    paginate_by = 9

    def get_queryset(self):
        entries = super().get_queryset()
        entries = entries.filter(user=self.request.user)
        entries = entries.select_related('game')
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

        entries = entries.prefetch_related('game__features')

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
