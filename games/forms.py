from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, PasswordResetForm, \
    SetPasswordForm
from django.contrib.auth import get_user_model

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

class GameAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        self.fields['username'].label = 'Имя пользователя'
        self.fields['username'].widget.attrs['placeholder'] = (
            'Введите имя пользователя'
        )

        self.fields['password'].label = 'Пароль'
        self.fields['password'].widget.attrs['placeholder'] = (
            'Введите пароль'
        )

class GameUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        self.fields['username'].label = 'Имя пользователя'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'
        self.fields['email'].label = 'Email'

        self.fields['username'].widget.attrs['placeholder'] = 'Придумайте имя пользователя'
        self.fields['password1'].widget.attrs['placeholder'] = 'Придумайте пароль'
        self.fields['password2'].widget.attrs['placeholder'] = 'Повторите пароль'
        self.fields['email'].widget.attrs['placeholder'] = 'Введите email'

        self.fields['email'].required = True

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Пользователь с таким email уже существует.')
        return email

class GamePasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        self.fields['old_password'].label = 'Текущий пароль'
        self.fields['old_password'].widget.attrs['placeholder'] = 'Введите текущий пароль'

        self.fields['new_password1'].label = 'Новый пароль'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Придумайте новый пароль'

        self.fields['new_password2'].label = 'Подтверждение пароля'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Повторите новый пароль'

class GamePasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        self.fields['email'].label = 'Email'
        self.fields['email'].widget.attrs['placeholder'] = 'Введите email, указанный при регистрации'

class GameSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        self.fields['new_password1'].label = 'Новый пароль'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Введите новый пароль'

        self.fields['new_password2'].label = 'Подтверждение пароля'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Подтвердите пароль'

class GameUserUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        self.fields['username'].label = 'Имя пользователя'
        self.fields['email'].label = 'Email'

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Пользователь с таким email уже существует.')
        return email

    class Meta:
        model = get_user_model()

        fields = ('username', 'email')