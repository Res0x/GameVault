from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from games.models import Game


class Command(BaseCommand):
    help = "Показать игры с незаполненными полями"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=10)

    def handle(self, *args, **options):
        limit = options["limit"]
        if limit < 1:
            raise CommandError("--limit должен быть положительным")

        games = Game.objects.all()

        games_with_null_fields = games.filter(
            Q(description='') |
            Q(genre='') |
            Q(platform='') |
            Q(developer='') |
            Q(cover='')
        )
        games_with_null_fields_count = games_with_null_fields.count()
        self.stdout.write(f'Игр всего: {games.count()}\nИгр с незаполненными полями: {games_with_null_fields_count.count()}')

        if games_with_null_fields.count():
            self.stdout.write('У следующих игр обнаружены незаполненные поля: ')
        for game in games_with_null_fields[:limit]:
            game_fields = {
                'описание': game.description,
                'жанр': game.genre,
                'платформы': game.platform,
                'разработчик': game.developer,
                'обложка': game.cover
            }
            res = game.title + '\nСледующие поля не заполнены: ' + ', '.join(i for i in game_fields if game_fields[i] == '')
            self.stdout.write(res)