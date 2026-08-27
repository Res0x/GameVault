from django.test import TestCase
from django.urls import reverse

from games.models import Game

class GameListViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.game = Game.objects.create(
            title='Hades',
            slug='hades',
            release_year=2020,
            genre='Roguelike',
            platform='PC',
            developer='Supergiant Games',
        )

        cls.other_game = Game.objects.create(
            title='Portal 2',
            slug='portal-2',
            release_year=2011,
            genre='Puzzle',
            platform='PC',
            developer='Valve',
        )

    def test_game_list_return_200(self):
        url = reverse('games:game_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_game_list_uses_expected_template(self):
        url = reverse('games:game_list')
        response = self.client.get(url)
        self.assertTemplateUsed(
            response,
            'games/game_list.html',
        )

    def test_game_in_response(self):
        url = reverse('games:game_list')
        response = self.client.get(url)
        self.assertIn(self.game, response.context['games'])

    def test_response_with_q_contains_game(self):
        url = reverse('games:game_list')
        response = self.client.get(url, {'q':'Hades'})
        games = list(response.context['games'])
        self.assertEqual(games, [self.game])