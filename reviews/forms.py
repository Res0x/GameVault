from django import forms

from reviews.models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = (
            'title',
            'body',
            'contains_spoilers'
        )
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class':'form-control'
                }
            ),
            'body': forms.Textarea(
                attrs={
                    'class':'form-control'
                }
            ),
            'contains_spoilers': forms.CheckboxInput(
                attrs={
                    'class':'form-check-input'
                }
            )
        }
        labels = {
            'title': 'Заголовок отзыва',
            'body': 'Текст отзыва',
            'contains_spoilers': 'Наличие спойлеров',
        }