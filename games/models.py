from django.db import models


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
    rating = models.PositiveSmallIntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    cover = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return self.title
