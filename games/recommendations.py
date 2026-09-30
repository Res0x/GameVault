from games.models import Game


def _platforms(value):
    platforms = set()

    for raw_platform in value.split(","):
        platform = raw_platform.strip().casefold()
        if platform:
            platforms.add(platform)

    return platforms


def _similarity(first, second):
    if not first or not second:
        return 0.0

    return len(first & second) / len(first | second)


def recommendations(game):
    game_features = {feature.pk for feature in game.features.all()}
    game_platforms = _platforms(game.platform)
    game_genre = game.genre.strip().casefold()
    game_developer = game.developer.strip().casefold()

    best = []

    other_games = (
        Game.objects
        .exclude(pk=game.pk)
        .prefetch_related("features")
        .iterator(chunk_size=200)
    )

    for other_game in other_games:
        other_features = {feature.pk for feature in other_game.features.all()}
        other_platforms = _platforms(other_game.platform)
        genre_matches = bool(game_genre) and game_genre == other_game.genre.strip().casefold()
        developer_matches = bool(game_developer) and game_developer == other_game.developer.strip().casefold()
        year_score = max(0, 1 - abs(other_game.release_year - game.release_year) / 10)
        score = (
            4 * _similarity(game_features, other_features)
            + 2 * genre_matches
            + _similarity(game_platforms, other_platforms)
            + developer_matches
            + year_score
        )
        if score <= 0:
            continue
        best.append((score, other_game))
        best.sort(
            key=lambda item: (
                -item[0],
                -item[1].release_year,
                item[1].title.casefold(),
                item[1].pk,
            )
        )
        if len(best) > 2:
            best.pop()

    return [other_game for _, other_game in best]