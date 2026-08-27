from datetime import date

from django.test import TestCase

from games.models import Game


class GameModelTests(TestCase):

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

        Game.objects.create(
            title='Alan Wake 2',
            slug='alan-wake-2',
            release_year=2023,
            genre='Survival Horror',
            platform='PC, PlayStation, Xbox',
            developer='Remedy Entertainment',
        )

        Game.objects.create(
            title="Baldur's Gate 3",
            slug='baldurs-gate-3',
            release_year=2023,
            genre='RPG',
            platform='PC, PlayStation, Xbox',
            developer='Larian Studios',
        )
        
        Game.objects.create(
            title='Mass Effect Legendary Edition',
            slug='mass-effect-legendary-edition',
            release_year=2021,
            genre='RPG',
            platform='PC, PlayStation, Xbox',
            developer='BioWare',
        )

    def test_game_representation(self):
        game = self.game

        result = str(game)

        self.assertEqual(result, 'Hades')

    def test_game_sort(self):
        games = Game.objects.all()
        titles = [game.title for game in games]
        answer = ['Alan Wake 2',
                  "Baldur's Gate 3",
                  'Mass Effect Legendary Edition',
                  'Hades']
        self.assertEqual(titles, answer)

    def test_orm_create_bypasses_form_release_year_validation(self):
        future_year = date.today().year + 100

        game = Game.objects.create(
            title='Future Game',
            slug='future-game',
            release_year=future_year,
            genre='RPG',
            platform='PC',
            developer='Test Developer',
        )

        self.assertEqual(game.release_year, future_year)