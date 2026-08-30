from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from games.models import Game
from library.models import LibraryEntry


User = get_user_model()


class LibraryEntryDetailViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            username='entry-owner',
        )
        cls.other_user = User.objects.create_user(
            username='entry-other-user',
        )

        cls.game = Game.objects.create(
            title='Hades',
            slug='hades-entry-detail-test',
            release_year=2020,
            genre='Roguelike',
            platform='PC',
            developer='Supergiant Games',
            added_by=cls.owner,
        )
        cls.game_without_entry = Game.objects.create(
            title='Portal 2',
            slug='portal-2-entry-detail-test',
            release_year=2011,
            genre='Puzzle',
            platform='PC',
            developer='Valve',
            added_by=cls.owner,
        )
        cls.other_game = Game.objects.create(
            title='Control',
            slug='control-entry-detail-test',
            release_year=2019,
            genre='Action',
            platform='PC',
            developer='Remedy Entertainment',
            added_by=cls.other_user,
        )

        cls.entry = LibraryEntry.objects.create(
            user=cls.owner,
            game=cls.game,
            status=LibraryEntry.Status.PLANNED,
        )
        cls.other_entry = LibraryEntry.objects.create(
            user=cls.other_user,
            game=cls.other_game,
            status=LibraryEntry.Status.PLANNED,
        )

    def test_anonymous_user_is_redirected_from_entry_detail(self):
        url = reverse(
            'library:library_entry_detail',
            kwargs={'pk': self.entry.pk},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('next=', response.url)

    def test_owner_can_open_entry_detail(self):
        self.client.force_login(self.owner)
        url = reverse(
            'library:library_entry_detail',
            kwargs={'pk': self.entry.pk},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'library/library_entry_detail.html',
        )
        self.assertEqual(response.context['entry'], self.entry)

    def test_user_cannot_open_another_users_entry(self):
        self.client.force_login(self.owner)
        url = reverse(
            'library:library_entry_detail',
            kwargs={'pk': self.other_entry.pk},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_update_redirects_to_updated_entry_detail(self):
        self.client.force_login(self.owner)
        update_url = reverse(
            'library:library_entry_edit',
            kwargs={'pk': self.entry.pk},
        )
        detail_url = reverse(
            'library:library_entry_detail',
            kwargs={'pk': self.entry.pk},
        )

        response = self.client.post(
            update_url,
            {
                'status': LibraryEntry.Status.PLANNED,
                'rating': '',
                'is_favourite': 'on',
                'notes': 'Вернуться к игре позже.',
                'started_at': '',
                'completed_at': '',
            },
        )

        self.assertRedirects(response, detail_url)
        self.entry.refresh_from_db()
        self.assertTrue(self.entry.is_favourite)
        self.assertEqual(
            self.entry.notes,
            'Вернуться к игре позже.',
        )

    def test_add_redirects_to_detail_and_does_not_create_duplicate(self):
        self.client.force_login(self.owner)
        add_url = reverse(
            'library:library_entry_add',
            kwargs={'game_slug': self.game_without_entry.slug},
        )

        first_response = self.client.post(add_url)
        entry = LibraryEntry.objects.get(
            user=self.owner,
            game=self.game_without_entry,
        )
        detail_url = reverse(
            'library:library_entry_detail',
            kwargs={'pk': entry.pk},
        )

        self.assertRedirects(first_response, detail_url)

        second_response = self.client.post(add_url)

        self.assertRedirects(second_response, detail_url)
        self.assertEqual(
            LibraryEntry.objects.filter(
                user=self.owner,
                game=self.game_without_entry,
            ).count(),
            1,
        )


class LibraryEntryListOrderingTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='ordering-user',
        )

        games = [
            Game.objects.create(
                title=f'Ordering Game {number}',
                slug=f'ordering-game-{number}',
                release_year=2020 + number,
                genre='Test',
                platform='PC',
                developer='Test Developer',
                added_by=cls.user,
            )
            for number in range(1, 5)
        ]

        cls.favourite_old = LibraryEntry.objects.create(
            user=cls.user,
            game=games[0],
            is_favourite=True,
        )
        cls.favourite_new = LibraryEntry.objects.create(
            user=cls.user,
            game=games[1],
            is_favourite=True,
        )
        cls.regular_old = LibraryEntry.objects.create(
            user=cls.user,
            game=games[2],
            is_favourite=False,
        )
        cls.regular_new = LibraryEntry.objects.create(
            user=cls.user,
            game=games[3],
            is_favourite=False,
        )

        now = timezone.now()
        LibraryEntry.objects.filter(
            pk=cls.favourite_old.pk,
        ).update(created_at=now - timedelta(days=4))
        LibraryEntry.objects.filter(
            pk=cls.favourite_new.pk,
        ).update(created_at=now - timedelta(days=3))
        LibraryEntry.objects.filter(
            pk=cls.regular_old.pk,
        ).update(created_at=now - timedelta(days=2))
        LibraryEntry.objects.filter(
            pk=cls.regular_new.pk,
        ).update(created_at=now - timedelta(days=1))

    def test_entries_are_ordered_by_favourite_then_creation_date(self):
        self.client.force_login(self.user)
        url = reverse('library:library_list')

        response = self.client.get(url)
        entries = list(response.context['entries'])

        self.assertEqual(
            entries,
            [
                self.favourite_new,
                self.favourite_old,
                self.regular_new,
                self.regular_old,
            ],
        )
