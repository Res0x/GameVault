from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models import ProtectedError

from library.models import LibraryEntry
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

User = get_user_model()


class GameDeleteViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='game-delete-user',
        )

        delete_permission = Permission.objects.get(
            content_type__app_label='games',
            codename='delete_game',
        )
        cls.user.user_permissions.add(delete_permission)

        cls.free_game = Game.objects.create(
            title='Free Game',
            slug='free-game',
            release_year=2020,
            added_by=cls.user,
        )

        cls.protected_game = Game.objects.create(
            title='Protected Game',
            slug='protected-game',
            release_year=2021,
            added_by=cls.user,
        )

        cls.library_entry = LibraryEntry.objects.create(
            user=cls.user,
            game=cls.protected_game,
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_delete_page_allows_game_without_library_entries(self):
        url = reverse(
            'games:game_delete',
            kwargs={'game_slug': self.free_game.slug},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['library_entries_count'],
            0,
        )
        self.assertContains(
            response,
            'class="button button-danger"',
        )

    def test_delete_page_blocks_game_with_library_entries(self):
        url = reverse(
            'games:game_delete',
            kwargs={'game_slug': self.protected_game.slug},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['library_entries_count'],
            1,
        )
        self.assertNotContains(
            response,
            'class="button button-danger"',
        )

    def test_game_without_library_entries_can_be_deleted(self):
        url = reverse(
            'games:game_delete',
            kwargs={'game_slug': self.free_game.slug},
        )

        response = self.client.post(url)

        self.assertRedirects(
            response,
            reverse('games:game_list'),
        )
        self.assertFalse(
            Game.objects.filter(pk=self.free_game.pk).exists(),
        )

    def test_game_with_library_entries_is_not_deleted(self):
        url = reverse(
            'games:game_delete',
            kwargs={'game_slug': self.protected_game.slug},
        )

        response = self.client.post(url)

        self.assertRedirects(
            response,
            reverse(
                'games:game_detail',
                kwargs={'game_slug': self.protected_game.slug},
            ),
        )
        self.assertTrue(
            Game.objects.filter(pk=self.protected_game.pk).exists(),
        )
        self.assertTrue(
            LibraryEntry.objects.filter(
                pk=self.library_entry.pk,
            ).exists(),
        )

    def test_protect_prevents_model_deletion(self):
        with self.assertRaises(ProtectedError):
            self.protected_game.delete()

        self.assertTrue(
            Game.objects.filter(pk=self.protected_game.pk).exists(),
        )