from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.test import TestCase

from games.models import Game
from library.models import LibraryEntry


User = get_user_model()


class LibraryEntryModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='library-test-user',
        )
        cls.other_user = User.objects.create_user(
            username='library-other-user',
        )

        cls.game = Game.objects.create(
            title='Hades',
            slug='hades-test',
            release_year=2020,
            genre='Roguelike',
            platform='PC',
            developer='Supergiant Games',
            added_by=cls.user,
        )
        cls.other_game = Game.objects.create(
            title='Portal 2',
            slug='portal-2-test',
            release_year=2011,
            genre='Puzzle',
            platform='PC',
            developer='Valve',
            added_by=cls.user,
        )

        cls.started_at = date(2025, 1, 10)
        cls.completed_at = date(2025, 1, 20)

    def entry_data(self, **overrides):
        data = {
            'user': self.user,
            'game': self.game,
            'status': LibraryEntry.Status.PLANNED,
            'rating': None,
            'started_at': None,
            'completed_at': None,
        }
        data.update(overrides)
        return data

    def build_entry(self, **overrides):
        return LibraryEntry(
            **self.entry_data(**overrides),
        )

    def create_entry(self, **overrides):
        return LibraryEntry.objects.create(
            **self.entry_data(**overrides),
        )

    def test_model_validation_library_entry_completed_without_date(self):
        entry = self.build_entry(status=LibraryEntry.Status.COMPLETED)

        with self.assertRaises(ValidationError) as context:
            entry.full_clean()

        self.assertIn('completed_at', context.exception.message_dict)

    def test_model_validation_uncompleted_entry_with_date(self):
        entry = self.build_entry(status=LibraryEntry.Status.PLANNED, completed_at=self.completed_at)

        with self.assertRaises(ValidationError) as context:
            entry.full_clean()

        self.assertIn('completed_at', context.exception.message_dict)

    def test_model_validation_rating_forbidden_for_playing(self):
        entry = self.build_entry(status=LibraryEntry.Status.PLAYING, rating=10)

        with self.assertRaises(ValidationError) as context:
            entry.full_clean()

        self.assertIn('rating', context.exception.message_dict)

    def test_model_validation_completed_at_less_than_started_at(self):
        entry = self.build_entry(status= LibraryEntry.Status.COMPLETED, started_at=self.completed_at, completed_at=self.started_at)
        with self.assertRaises(ValidationError) as context:
            entry.full_clean()

        self.assertIn('completed_at', context.exception.message_dict)

    def test_database_constraint_rating_0(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_entry(rating=0, status=LibraryEntry.Status.COMPLETED, completed_at=self.completed_at)

    def test_database_constraint_rating_11(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_entry(rating=11, status=LibraryEntry.Status.COMPLETED, completed_at=self.completed_at)

    def test_database_constraint_started_at_bigger_than_completed_at(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_entry(status=LibraryEntry.Status.COMPLETED, started_at=self.completed_at, completed_at=self.started_at)

    def test_database_constraint_completed_game_without_completed_at(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_entry(status=LibraryEntry.Status.COMPLETED)

    def test_database_constraint_uncompleted_game_with_completed_at(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_entry(completed_at=self.completed_at)

    def test_database_constraint_playing_with_rating(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_entry(rating=10, status=LibraryEntry.Status.PLAYING)

    def test_database_constraint_unique_user_and_game(self):
        self.create_entry()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_entry()

    def test_planned_without_dates_and_rating(self):

        before_test = LibraryEntry.objects.all().count()

        self.create_entry(status=LibraryEntry.Status.PLANNED)

        after_test = LibraryEntry.objects.all()

        self.assertEqual(before_test + 1, after_test.count())

    def test_completed_with_dates_and_rating(self):

        before_test = LibraryEntry.objects.all().count()

        self.create_entry(status=LibraryEntry.Status.COMPLETED, rating=10,
                          started_at=self.started_at, completed_at=self.completed_at)

        after_test = LibraryEntry.objects.all()

        self.assertEqual(before_test + 1, after_test.count())

    def test_dropped_with_rating_and_without_completed_at(self):

        before_test = LibraryEntry.objects.all().count()

        self.create_entry(status=LibraryEntry.Status.DROPPED, rating=1)

        after_test = LibraryEntry.objects.all()

        self.assertEqual(before_test + 1, after_test.count())
