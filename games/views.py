from django.shortcuts import render
from django.http import Http404

GAME_DETAILS = {
    'witcher-3': {
        'slug': 'witcher-3',
        'title': 'The Witcher 3: Wild Hunt',
        'subtitle': 'Большое сюжетное приключение в мрачном фэнтезийном мире',
        'genre': 'RPG',
        'platform': 'PC',
        'status': 'Пройдено',
        'rating': 10,
        'developer': 'CD Projekt Red',
        'release_year': 2015,
        'playtime': '120 часов',
        'cover': 'games/images/witcher-3.svg',
        'cover_caption': 'Обложка The Witcher 3: Wild Hunt',
        'description': (
            'История охотника на чудовищ, который путешествует по открытому '
            'миру, выполняет заказы и принимает решения, влияющие на сюжет.'
        ),
        'highlights': [
            'Большой открытый мир с самостоятельными историями.',
            'Развитая система заданий и диалогов.',
            'Решения игрока влияют на развитие событий.',
            'Большое количество дополнительного контента.',
        ],
        'recommendation_slugs': [
            'cyberpunk-2077',
            'hollow-knight',
        ],
    },
    'cyberpunk-2077': {
        'slug': 'cyberpunk-2077',
        'title': 'Cyberpunk 2077',
        'subtitle': 'Футуристическая RPG о наемнике из Найт-Сити',
        'genre': 'Action RPG',
        'platform': 'PC',
        'status': 'Прохожу',
        'rating': 9,
        'developer': 'CD Projekt Red',
        'release_year': 2020,
        'playtime': '85 часов',
        'cover': 'games/images/cyberpunk-2077.svg',
        'cover_caption': 'Обложка Cyberpunk 2077',
        'description': (
            'Приключение в технологичном мегаполисе, где игрок развивает '
            'персонажа, выполняет задания и выбирает собственный стиль игры.'
        ),
        'highlights': [
            'Атмосферный город с большим количеством районов.',
            'Разные способы выполнения заданий.',
            'Гибкая система развития персонажа.',
            'Сюжетные и дополнительные цепочки заданий.',
        ],
        'recommendation_slugs': [
            'witcher-3',
            'hollow-knight',
        ],
    },
    'hollow-knight': {
        'slug': 'hollow-knight',
        'title': 'Hollow Knight',
        'subtitle': 'Исследование таинственного подземного королевства',
        'genre': 'Metroidvania',
        'platform': 'PC',
        'status': 'Хочу пройти',
        'rating': None,
        'developer': 'Team Cherry',
        'release_year': 2017,
        'playtime': 'Не указано',
        'cover': 'games/images/hollow-knight.svg',
        'cover_caption': 'Обложка Hollow Knight',
        'description': (
            'Атмосферное приключение с исследованием связанных локаций, '
            'сражениями, поиском секретов и постепенным открытием новых путей.'
        ),
        'highlights': [
            'Связанный мир с большим количеством секретов.',
            'Выразительный визуальный стиль.',
            'Разнообразные противники и боссы.',
            'Постепенное открытие новых способностей.',
        ],
        'recommendation_slugs': [
            'witcher-3',
            'cyberpunk-2077',
        ],
    },
}

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
    search_query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    normalized_query = search_query.lower()
    games = [
        {
            'id': 1,
            'title': 'The Witcher 3',
            'genre': 'RPG',
            'platform': 'PC',
            'status': 'Пройдено',
            'status_code': 'completed',
            'rating': 10,
            'cover': 'games/images/witcher-3.svg',
            'cover_caption': 'Фэнтезийное приключение в открытом мире',
            'slug': 'witcher-3',
        },
        {
            'id': 2,
            'title': 'Cyberpunk 2077',
            'genre': 'RPG',
            'platform': 'PC',
            'status': 'Прохожу',
            'status_code': 'playing',
            'rating': 9,
            'cover': 'games/images/cyberpunk-2077.svg',
            'cover_caption': 'История в неоновом мегаполисе будущего',
            'slug': 'cyberpunk-2077',
        },
        {
            'id': 3,
            'title': 'Hollow Knight',
            'genre': 'Metroidvania',
            'platform': 'PC',
            'status': 'Хочу пройти',
            'status_code': 'planned',
            'rating': None,
            'cover': 'games/images/hollow-knight.svg',
            'cover_caption': 'Путешествие по мрачному подземному королевству',
            'slug': 'hollow-knight',
        },
    ]
    statuses = ('planned', 'playing', 'completed')
    if normalized_query:
        games = [game for game in games
                 if normalized_query in game['title'].lower()
                 or normalized_query in game['genre'].lower()]
    if status not in statuses:
        status = ''
    if status:
        games = [game for game in games if game['status_code'] == status]
    context = {
        'page_title': 'Список игр',
        'games': games,
        'games_count': len(games),
        'q': search_query,
        'selected_status': status,
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

    errors = {}

    form_data = {
        'title': '',
        'genre': '',
        'platform': '',
        'status': '',
        'play_mode': '',
        'features': [],
        'rating': '',
        'description': '',
    }

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

    play_mode_labels = {
        'single': 'Одиночная игра',
        'multiplayer': 'Мультиплеер',
        'both': 'Одиночная игра и мультиплеер',
    }

    feature_labels = {
        'story': 'Сюжетная игра',
        'open_world': 'Открытый мир',
        'coop': 'Кооператив',
    }

    if request.method == 'POST':
        platform = request.POST.get('platform', '')
        status = request.POST.get('status', '')
        play_mode = request.POST.get('play_mode', '')
        selected_features = request.POST.getlist('features')
        title = request.POST.get('title', '')
        genre = request.POST.get('genre', '')
        rating = request.POST.get('rating', '')
        description = request.POST.get('description', '')

        form_data = {
            'title': title,
            'genre': genre,
            'platform': platform,
            'status': status,
            'play_mode': play_mode,
            'features': selected_features,
            'rating': rating,
            'description': description,
        }

        platform = platform.strip()
        status = status.strip()
        title = title.strip()
        genre = genre.strip()
        rating = rating.strip()
        description = description.strip()

        feature_names = [
            feature_labels[feature]
            for feature in selected_features
            if feature in feature_labels
        ]
        if not title:
            errors['title'] = 'Введите название игры.'

        if not genre:
            errors['genre'] = 'Введите жанр игры.'

        if platform not in platform_labels:
            errors['platform'] = 'Выберите допустимую платформу.'

        if status not in status_labels:
            errors['status'] = 'Выберите допустимый статус.'

        if not errors:
            submitted_game = {
                'title': title,
                'genre': genre,
                'platform_display': platform_labels.get(platform, ''),
                'status_display': status_labels.get(status, ''),
                'play_mode_display': play_mode_labels.get(play_mode, ''),
                'features_display': (
                    ', '.join(feature_names)
                    if feature_names
                    else 'Не выбраны'
                ),
                'rating': rating,
                'description': description,
            }

    context = {
        'page_title': 'Добавить игру',
        'submitted_game': submitted_game,
        'errors': errors,
        'form_data': form_data,
    }

    return render(request, 'games/game_create.html', context)

def game_detail(request, game_slug):
    game = GAME_DETAILS.get(game_slug)

    if game is None:
        raise Http404('Игра не найдена')

    recommendations = [
        GAME_DETAILS[slug]
        for slug in game['recommendation_slugs']
        if slug in GAME_DETAILS
    ]

    context = {
        'page_title': game['title'],
        'game': game,
        'recommendations': recommendations,
    }

    return render(request, 'games/game_detail.html', context)