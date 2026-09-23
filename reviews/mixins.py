class UserReviewsMixin:

    def get_queryset(self):
        qs = super().get_queryset().filter(author=self.request.user).select_related('game')
        return qs
