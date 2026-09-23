from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib import messages

from reviews.forms import ReviewForm
from reviews.models import Review
from reviews.mixins import UserReviewsMixin
from games.models import Game


class ReviewCreateView(LoginRequiredMixin, CreateView):
    form_class = ReviewForm
    model = Review
    template_name = 'reviews/review_form.html'

    def get_success_url(self):
        return reverse('games:game_detail', kwargs={'game_slug': self.get_game().slug}) + '#reviews'

    def form_valid(self, form):
        game = self.get_game()
        review_exists = Review.objects.filter(game=game, author=self.request.user).exists()
        if review_exists:
            messages.info(self.request, 'Вы уже писали отзыв на эту игру!')
            url = reverse('games:game_detail', kwargs={'game_slug': self.get_game().slug}) + '#reviews'
            return redirect(url)
        else:
            form.instance.author = self.request.user
            form.instance.game = self.get_game()
            response = super().form_valid(form)

            messages.success(self.request, 'Отзыв успешно добавлен!')

            return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.get_game()
        context['page_title'] = f'Добавление отзыва на игру {self.get_game().title}'
        context['form_heading'] = 'Создание отзыва'
        context['submit_text'] = 'Опубликовать отзыв'
        return context

    def get_game(self):
        if hasattr(self, 'game'):
            return getattr(self, 'game')
        game = get_object_or_404(Game, slug=self.kwargs['game_slug'])
        self.game = game
        return self.game

class ReviewUpdateView(LoginRequiredMixin, UserReviewsMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'

    def get_success_url(self):
        return reverse('games:game_detail', kwargs={'game_slug': self.object.game.slug}) + '#reviews'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.info(self.request, 'Отзыв обновлен')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Редактирование отзыва'
        context['form_heading'] = 'Изменение отзыва'
        context['submit_text'] = 'Сохранить изменения'
        context['game'] = self.object.game

        return context

class ReviewDeleteView(LoginRequiredMixin, UserReviewsMixin, DeleteView):
    model = Review
    template_name = 'reviews/review_confirm_delete.html'

    def get_success_url(self):
        return reverse('games:game_detail', kwargs={'game_slug': self.object.game.slug}) + '#reviews'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.info(self.request, 'Отзыв успешно удален!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.object
        return context