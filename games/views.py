from django.shortcuts import render


def home(request):
    context = {
        'page_title': 'GameVault',
        'subtitle': 'Личная библиотека видеоигр',
        'description': (
            'Здесь можно хранить игры, которые ты проходишь, '
            'уже прошел или только планируешь пройти.'
        ),
        'total_games': 12,
        'playing_games': 3,
        'completed_games': 5,
        'planned_games': 4,
        'featured_game': {
            'title': 'The Witcher 3',
            'description': (
                'Сюжетная ролевая игра с открытым миром, '
                'сложными заданиями и последствиями принятых решений.'
            ),
            'status': 'Пройдено',
            'rating': 10,
            'cover': 'games/images/witcher-3.svg',
            'cover_caption': 'Фэнтезийное приключение в открытом мире',
        },
    }

    return render(request, 'games/home.html', context)


def game_list(request):
    games = [
        {
            'id': 1,
            'title': 'The Witcher 3',
            'genre': 'RPG',
            'platform': 'PC',
            'status': 'Пройдено',
            'rating': 10,
            'cover': 'games/images/witcher-3.svg',
            'cover_caption': 'Фэнтезийное приключение в открытом мире',
        },
        {
            'id': 2,
            'title': 'Cyberpunk 2077',
            'genre': 'RPG',
            'platform': 'PC',
            'status': 'Прохожу',
            'rating': 9,
            'cover': 'games/images/cyberpunk-2077.svg',
            'cover_caption': 'История в неоновом мегаполисе будущего',
        },
        {
            'id': 3,
            'title': 'Hollow Knight',
            'genre': 'Metroidvania',
            'platform': 'PC',
            'status': 'Хочу пройти',
            'rating': None,
            'cover': 'games/images/hollow-knight.svg',
            'cover_caption': 'Путешествие по мрачному подземному королевству',
        },
    ]

    context = {
        'page_title': 'Список игр',
        'games': games,
    }

    return render(request, 'games/game_list.html', context)

def ratings(request):
    rated_games = [
        {
            'title': 'The Witcher 3',
            'genre': 'RPG',
            'status': 'Пройдено',
            'rating': 10,
        },
        {
            'title': 'Cyberpunk 2077',
            'genre': 'RPG',
            'status': 'Прохожу',
            'rating': 9,
        },
        {
            'title': 'Hades',
            'genre': 'Roguelike',
            'status': 'Пройдено',
            'rating': 9,
        },
        {
            'title': 'Disco Elysium',
            'genre': 'RPG',
            'status': 'Пройдено',
            'rating': 8,
        },
        {
            'title': 'Control',
            'genre': 'Action',
            'status': 'Пройдено',
            'rating': 8,
        },
    ]

    context = {
        'page_title': 'Рейтинг игр',
        'rated_games': rated_games,
    }

    return render(request, 'games/ratings.html', context)

def game_create(request):
    submitted_game = None

    platform_labels = {
        'pc': 'PC',
        'playstation': 'PlayStation',
        'xbox': 'Xbox',
        'switch': 'Nintendo Switch',
    }

    status_labels = {
        'planned': 'Хочу пройти',
        'playing': 'Прохожу',
        'completed': 'Пройдено',
    }

    if request.method == 'POST':
        platform = request.POST.get('platform', '')
        status = request.POST.get('status', '')

        submitted_game = {
            'title': request.POST.get('title', '').strip(),
            'genre': request.POST.get('genre', '').strip(),
            'platform': platform,
            'platform_display': platform_labels.get(platform, ''),
            'status': status,
            'status_display': status_labels.get(status, ''),
            'rating': request.POST.get('rating', ''),
            'description': request.POST.get('description', '').strip(),
        }

    context = {
        'page_title': 'Добавить игру',
        'submitted_game': submitted_game,
    }

    return render(request, 'games/game_create.html', context)