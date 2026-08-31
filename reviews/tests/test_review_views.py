from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from games.models import Game
from reviews.models import Review


User = get_user_model()


class ReviewCreateViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='review-author',
            password='test-password',
        )
        cls.other_user = User.objects.create_user(
            username='other-review-author',
            password='test-password',
        )
        cls.game = Game.objects.create(
            title='Hades',
            slug='hades-review-test',
            release_year=2020,
            genre='Roguelike',
            platform='PC',
            developer='Supergiant Games',
            added_by=cls.user,
        )
        cls.other_game = Game.objects.create(
            title='Portal 2',
            slug='portal-2-review-test',
            release_year=2011,
            genre='Puzzle',
            platform='PC',
            developer='Valve',
            added_by=cls.user,
        )

    def setUp(self):
        self.create_url = reverse(
            'reviews:review_create',
            kwargs={'game_slug': self.game.slug},
        )
        self.game_detail_url = reverse(
            'games:game_detail',
            kwargs={'game_slug': self.game.slug},
        )
        self.valid_data = {
            'title': 'Отличная игра',
            'body': 'Быстрые сражения и интересная история.',
        }

    def test_anonymous_user_cannot_open_review_form(self):
        response = self.client.get(self.create_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('next=', response.url)
        self.assertEqual(Review.objects.count(), 0)

    def test_authenticated_user_can_open_review_form(self):
        self.client.force_login(self.user)

        response = self.client.get(self.create_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reviews/review_form.html')
        self.assertEqual(response.context['game'], self.game)

    def test_valid_post_creates_review_and_redirects_to_reviews_section(self):
        self.client.force_login(self.user)

        response = self.client.post(self.create_url, self.valid_data)

        review = Review.objects.get()
        self.assertEqual(review.author, self.user)
        self.assertEqual(review.game, self.game)
        self.assertEqual(review.title, self.valid_data['title'])
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'{self.game_detail_url}#reviews')

    def test_author_and_game_from_post_data_are_ignored(self):
        self.client.force_login(self.user)
        data = {
            **self.valid_data,
            'author': self.other_user.pk,
            'game': self.other_game.pk,
        }

        self.client.post(self.create_url, data)

        review = Review.objects.get()
        self.assertEqual(review.author, self.user)
        self.assertEqual(review.game, self.game)

    def test_invalid_post_does_not_create_review_and_keeps_form_data(self):
        self.client.force_login(self.user)
        data = {
            'title': '',
            'body': 'Этот текст должен остаться в форме.',
        }

        response = self.client.post(self.create_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Review.objects.count(), 0)
        self.assertIn('title', response.context['form'].errors)
        self.assertEqual(
            response.context['form']['body'].value(),
            data['body'],
        )

    def test_duplicate_review_is_not_created_and_message_is_shown(self):
        Review.objects.create(
            author=self.user,
            game=self.game,
            title='Первый отзыв',
            body='Первый текст отзыва.',
        )
        self.client.force_login(self.user)

        response = self.client.post(self.create_url, self.valid_data)

        messages = [
            str(message)
            for message in get_messages(response.wsgi_request)
        ]
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'{self.game_detail_url}#reviews')
        self.assertIn('Вы уже писали отзыв на эту игру!', messages)

    def test_another_user_can_review_the_same_game(self):
        Review.objects.create(
            author=self.user,
            game=self.game,
            title='Отзыв первого пользователя',
            body='Первый пользователь уже оставил отзыв.',
        )
        self.client.force_login(self.other_user)

        response = self.client.post(self.create_url, self.valid_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 2)
        self.assertTrue(
            Review.objects.filter(
                author=self.other_user,
                game=self.game,
            ).exists()
        )


class GameDetailReviewsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='public-review-author',
        )
        cls.game = Game.objects.create(
            title='Hades',
            slug='hades-public-review-test',
            release_year=2020,
            genre='Roguelike',
            platform='PC',
            developer='Supergiant Games',
            added_by=cls.user,
        )
        cls.review = Review.objects.create(
            author=cls.user,
            game=cls.game,
            title='Публичный отзыв',
            body='Этот отзыв должен увидеть любой посетитель.',
            contains_spoilers=True,
        )

    def test_anonymous_user_can_see_review_on_game_detail_page(self):
        url = reverse(
            'games:game_detail',
            kwargs={'game_slug': self.game.slug},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.review, response.context['reviews'])
        self.assertIsNone(response.context['user_review'])
        self.assertContains(response, self.review.title)
        self.assertContains(response, self.review.body)
