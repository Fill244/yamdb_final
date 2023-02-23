from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from api.v1.custom_filter import TitleFilter
from api.v1.custom_mixin import CreateListDestroyViewSet
from api.mail_utils import send_email
from api.v1.permissions import (AdminModeratorAuthorPermission, AdminOnly,
                                IsAdminUserOrReadOnly)
from api.v1.serializer import (CategorySerializer, CommentSerializer,
                               GenreSerializer, GetTokenSerializer,
                               RegisterSerializer, ReviewSerializer,
                               TitlesReadSerializer, TitlesWriteSerializer,
                               UserSelfSerializer, UserSerializer)
from reviews.models import Category, Genre, Review, Title


User = get_user_model()


class ReviewViewSet(ModelViewSet):
    """
    Получение и добавление отзывов к шедевру
    GET - доступно всем
    POST - user может добавить только один отзыв на произведение
    PATCH, PUT, DELETE - автор отзыва, модератор, админ
    """
    serializer_class = ReviewSerializer
    permission_classes = (AdminModeratorAuthorPermission,
                          IsAuthenticatedOrReadOnly)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.review.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(ModelViewSet):
    """
    Комментарии к отзывам
    GET - доступно всем
    POST - аутентифицированный юзер
    PATCH, PUT, DELETE - автор отзыва, модератор, админ
    """
    serializer_class = CommentSerializer
    permission_classes = (AdminModeratorAuthorPermission,
                          IsAuthenticatedOrReadOnly)

    def get_queryset(self):
        review = get_object_or_404(
            Review, pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class CategoryViewSet(CreateListDestroyViewSet):
    """
    GET /categories/ - список всех категорий, доступно всем
    GET /categories/?search=name - доступно всем
    POST /categories/ - только admin
        params = {"name": string, "slug": string}
    DELETE /categories/slug/ - только admin
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    """
    GET /genres/ - список всех жанров, доступно всем
    GET /genres/?search=name - доступно всем
    POST /genres/ - только admin
        params = {"name": string, "slug": string}
    DELETE /genres/slug/ - только admin
        """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitlesViewSet(ModelViewSet):
    """
    Получение списка всех произведений со средним рейтингом.
    GET - доступно без токена.
    POST, PUT, PATCH, DELETE - только администратор.
    """
    filterset_class = TitleFilter
    queryset = Title.objects.annotate(rating=Avg('review__score')).all()
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (filters.DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitlesReadSerializer
        return TitlesWriteSerializer


class UsersViewSet(ModelViewSet):
    """
    GET, POST: /users/ - admin
    GET, POST, PATCH, DELETE: /users/username/ - admin
    GET, POST: /users/me/ - авторизованный пользователь
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, AdminOnly,)
    lookup_field = 'username'

    @action(
        methods=('GET', 'PATCH',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me')
    def get_current_user_info(self, request):
        serializer = UserSelfSerializer(
            request.user, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class EmailTokenObtainPairView(APIView):
    """
    POST: /auth/token/
    отправить код подтверждения и получить токен
    {"username": "string","confirmation_code": "string"}
    """

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = get_object_or_404(User, username=data['username'])

        if default_token_generator.check_token(
                user, data.get('confirmation_code')):
            token = RefreshToken.for_user(user).access_token

            return Response({'token': str(token)},
                            status=status.HTTP_201_CREATED)

        return Response(
            {'confirmation_code': 'Неверный код подтверждения!'},
            status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """
    POST: /auth/signup/
    получить код подтверждения на email
    {"email": "string","username": "string"}
    """
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):

            try:
                user, _ = User.objects.get_or_create(
                    username=request.data.get('username'),
                    email=request.data.get('email'))
            except IntegrityError:
                return Response({'error': ('Пользователь с похожим username'
                                           ' или email уже существует')},
                                status=status.HTTP_400_BAD_REQUEST)

            user.confirmation_code = default_token_generator.make_token(user)

            send_email(user)

            return Response(serializer.data, status.HTTP_200_OK)
