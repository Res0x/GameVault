from django import forms

from library.models import LibraryEntry


class LibraryEntryForm(forms.ModelForm):
    class Meta:
        model = LibraryEntry

        fields = (
            'status',
            'rating',
            'is_favourite',
            'notes',
            'started_at',
            'completed_at',
        )

        widgets = {
            'status': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
            'rating': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'is_favourite': forms.CheckboxInput(
                attrs={
                    'class': 'choice-input',
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                }
            ),
            'started_at': forms.DateInput(
                        format='%Y-%m-%d',
                        attrs={
                            'type': 'date',
                            'class': 'form-control',
                        },
                    ),
            'completed_at': forms.DateInput(
                        format='%Y-%m-%d',
                        attrs={
                            'type': 'date',
                            'class': 'form-control',
                        },
                    ),
        }
        labels = {
            'status': 'Статус',
            'rating': 'Рейтинг',
            'is_favourite': 'Избранное',
            'notes': 'Заметки',
            'started_at': 'Дата начала прохождения',
            'completed_at': 'Дата завершения прохождения',
        }
        help_texts = {
            'rating': 'Оценка от 1 до 10. Доступна только для пройденной или заброшенной игры.',
            'started_at': 'Фактическая дата начала игры.',
            'completed_at': 'Фактическая дата прохождения игры.',
            'notes': 'Личные впечатления и заметки, не более 500 символов.',
        }