from django.urls import include, path
from djoser import views
from rest_framework.routers import SimpleRouter

from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet, set_password)

router = SimpleRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('auth/token/login/', views.TokenCreateView.as_view(), name='login'),
    path(
        'auth/token/logout/',
        views.TokenDestroyView.as_view(),
        name='logout'
    ),
    path(
        'users/set_password/',
        set_password,
        name='set_password_profile'
    ),
    path('', include(router.urls)),
]
