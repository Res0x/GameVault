class UserEntriesMixin:

    def get_queryset(self):
        entries = super().get_queryset().for_user(self.request.user)
        return entries