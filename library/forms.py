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

    def clean(self):
        cleaned_data = super().clean()

        status = cleaned_data.get('status')
        started_at = cleaned_data.get('started_at')
        completed_at = cleaned_data.get('completed_at')
        rating = cleaned_data.get('rating')

        if (started_at and completed_at) and started_at > completed_at:
            self.add_error('completed_at', 'Дата завершения не может быть раньше даты начала!')

        if status == LibraryEntry.Status.COMPLETED and not completed_at:
            self.add_error('completed_at', 'Если вы прошли игру, то добавьте дату завершения!')
        if status is not None and status != LibraryEntry.Status.COMPLETED and completed_at:
            self.add_error('completed_at', 'У игры, которую вы не прошли не может быть даты прохождения!')
        if rating is not None and status is not None and status not in (LibraryEntry.Status.COMPLETED, LibraryEntry.Status.DROPPED):
            self.add_error('rating', 'Нельзя оценить игру, которую вы не прошли или не забросили.')

        return cleaned_data