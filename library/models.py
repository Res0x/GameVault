from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings
from django.db.models.deletion import PROTECT


class LibraryEntry(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='library_entries')
    game = models.ForeignKey('games.Game', on_delete=PROTECT, related_name='library_entries')

    class Status(models.TextChoices):
        PLANNED = 'planned', 'Хочу пройти'
        PLAYING = 'playing', 'Прохожу'
        PAUSED = 'paused', 'Отложено'
        COMPLETED = 'completed', 'Пройдено'
        DROPPED = 'dropped', 'Заброшено'

    status = models.CharField(choices=Status.choices, default=Status.PLANNED, max_length=10)
    rating = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    is_favourite = models.BooleanField(default=False)
    notes = models.TextField(blank=True, max_length=500)
    started_at = models.DateField(null=True, blank=True)
    completed_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):

        super().clean()

        errors = {}

        if self.completed_at is None and self.status == self.Status.COMPLETED:
            errors['completed_at'] = 'Для пройденной игры это поле обязательно'

        if self.completed_at is not None and self.status != self.Status.COMPLETED:
            errors['completed_at'] = 'Игру нужно пройти чтобы указать дату завершения'

        if self.rating is not None and self.status not in (self.Status.COMPLETED, self.Status.DROPPED):
            errors['rating'] = 'Оценка разрешена только для пройденной или заброшенной игры'

        if self.started_at is not None and self.completed_at is not None:
            if self.started_at > self.completed_at:
                errors['completed_at'] = 'Дата завершения игры не может быть раньше даты начала прохождения'

        if errors:
            raise ValidationError(errors)


    class Meta:
        ordering = ('-updated_at',)
        verbose_name = 'Библиотека пользователя'
        verbose_name_plural = 'Библиотеки пользователя'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'game'),
                name='unique_library_entry_per_user_game',
            ),
            models.CheckConstraint(
                condition=models.Q(rating__isnull=True) | (models.Q(rating__lte=10) & models.Q(rating__gte=1)),
                name='rating_between_1_and_10',
            ),
            models.CheckConstraint(
                condition=models.Q(started_at__isnull=True) | models.Q(completed_at__isnull=True) | models.Q(started_at__lte=models.F('completed_at')),
                name='game_started_earlier_than_completed_at',
            ),
            models.CheckConstraint(
                condition=(models.Q(status='completed') & models.Q(completed_at__isnull=False)) |
                          (~models.Q(status='completed') & models.Q(completed_at__isnull=True)),
                name='completed_game_have_completed_date'
            ),
            models.CheckConstraint(
                condition=models.Q(rating__isnull=True) |
                          models.Q(status__in=('completed', 'dropped')),
                name='rating_only_in_dropped_or_completed_game'
            ),
        ]

    def __str__(self):
        return f'{self.user.get_username()} — {self.game.title}'