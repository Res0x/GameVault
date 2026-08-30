from django.conf import settings
from django.db import models
from django.db.models import CASCADE, PROTECT


class Review(models.Model):

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE,
                               related_name='reviews')
    game = models.ForeignKey('games.Game', on_delete=PROTECT, related_name='reviews')
    title = models.CharField(max_length=150)
    body = models.TextField(max_length=3000)
    contains_spoilers = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name = 'Обзор'
        verbose_name_plural = 'Обзоры'
        constraints = [
            models.UniqueConstraint(fields=['author', 'game'],
                                    name='one_author_for_one_game_review'),
        ]

    def __str__(self):
        return f'{self.title} - {self.game} - {self.author}'