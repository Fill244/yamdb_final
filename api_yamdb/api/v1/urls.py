from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import (CategoryViewSet, CommentViewSet, UsersViewSet,
                          GenreViewSet, ReviewViewSet, RegisterView,
                          TitlesViewSet, EmailTokenObtainPairView)

v1_router = DefaultRouter()

v1_router.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='reviews')
v1_router.register(r'titles/(?P<title_id>\d+)/reviews/'
                   r'(?P<review_id>\d+)/comments',
                   CommentViewSet, basename='comment')
v1_router.register('titles', TitlesViewSet, basename='titles')
v1_router.register('categories', CategoryViewSet, basename='category')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('users', UsersViewSet, basename='users',)

auth_patterns = [
    path('token/', EmailTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('signup/', RegisterView.as_view(), name='signup')]

urlpatterns = (path('', include(v1_router.urls)),
               path('auth/', include(auth_patterns)),)
