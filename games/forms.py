from django import forms
from django.core.exceptions import ValidationError
from .models import Game
from datetime import date


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = (
            'title',
            'slug',
            'release_year',
            'genre',
            'platform',
            'developer',
            'rating',
            'status',
            'cover',
            'subtitle',
            'playtime',
            'description',
            'features',
        )
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'placeholder': 'Например, Hades',
                },
            ),
            'slug': forms.TextInput(
                attrs={
                    'placeholder': 'Например, hades',
                }
            ),
            'genre': forms.TextInput(
                attrs={
                    'placeholder': 'Например, Roguelike',
                }
            ),
            'platform': forms.TextInput(
                attrs={
                    'placeholder': 'Например, PC',
                }
            ),
            'developer': forms.TextInput(
                attrs={
                    'placeholder': 'Например, Supergiant Games',
                }
            ),
            'cover': forms.TextInput(
                attrs={
                    'placeholder': 'games/images/hades.svg',
                }
            ),
            'subtitle': forms.TextInput(
                attrs={
                    'placeholder': 'Короткое описание игры',
                }
            ),
            'playtime': forms.TextInput(
                attrs={
                    'placeholder': 'Например, 25 часов',
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'rows': 6,
                },
            ),
            'release_year': forms.NumberInput(),
            'rating': forms.NumberInput(),
            'features': forms.CheckboxSelectMultiple(
                attrs={
                    'class': 'choice-input',
                }
            )
        }
        labels = {
            'title': 'Название',
            'slug': 'Slug',
            'release_year': 'Год выпуска',
            'genre': 'Жанр',
            'platform': 'Платформа',
            'developer': 'Разработчик',
            'rating': 'Рейтинг',
            'status': 'Статус',
            'cover': 'Путь к обложке',
            'subtitle': 'Подзаголовок',
            'playtime': 'Время прохождения',
            'description': 'Описание',
            'features': 'Особенности',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'features':
                field.widget.attrs.update({
                    'class': 'form-control',
                })

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        return slug.lower()

    def clean_release_year(self):
        release_year = self.cleaned_data['release_year']
        max_year = date.today().year + 2
        if release_year > max_year:
            raise ValidationError(f'Максимальный год выпуска {max_year}.')
        return release_year

    def clean(self):
        cleaned_data = super().clean()

        status = cleaned_data.get('status')
        rating = cleaned_data.get('rating')
        if status == Game.Status.COMPLETED and rating in cleaned_data:
            self.add_error('rating',
                           'Для пройденной игры укажи рейтинг.')
        elif status != Game.Status.COMPLETED and rating is not None:
            self.add_error('rating',
                           'Нельзя оценить игру, которая еще не пройдена.')
        return cleaned_data