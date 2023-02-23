from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               mixins.ListModelMixin,
                               GenericViewSet):
    """Вьюсет для категорий и жанров."""
