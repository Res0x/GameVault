from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q


class Game(models.Model):

    class Status(models.TextChoices):
        PLANNED = 'planned', 'Хочу пройти'
        PLAYING = 'playing', 'Прохожу'
        COMPLETED = 'completed', 'Пройдено'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    release_year = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    genre = models.CharField(max_length=100, blank=True, default='')
    platform = models.CharField(max_length=100, blank=True, default='')
    developer = models.CharField(max_length=150, blank=True, default='')
    rating = models.PositiveSmallIntegerField(blank=True, null=True,
                                              validators=[
                                                  MinValueValidator(1),
                                                  MaxValueValidator(10)
                                              ])
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    cover = models.CharField(max_length=255, blank=True, default='')
    subtitle = models.CharField(max_length=255, blank=True, default='')
    playtime = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['-release_year', 'title']
        verbose_name = 'Игра'
        verbose_name_plural = 'Игры'
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(rating__isnull=True) |
                    (Q(rating__gte=1) & Q(rating__lte=10))
                ),
                name='game_rating_between_1_and_10'
            )
        ]

    def __str__(self):
        return self.title


class GameHighlight(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='highlights',
    )
    text = models.CharField(max_length=255)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['position', 'id']
        verbose_name = 'Особенность игры'
        verbose_name_plural = 'Особенности игры'

    def __str__(self):
        short_text = self.text[:40]

        if len(self.text) > 40:
            short_text += '...'

        return f'{self.game.title}: {short_text}'