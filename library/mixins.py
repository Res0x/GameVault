class UserEntriesMixin:

    def get_queryset(self):
        entries = super().get_queryset()
        entries = entries.filter(user=self.request.user)
        return entries