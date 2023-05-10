from io import StringIO

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.conf import settings
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Subscription, Tag)
from users.models import CustomUser

from .filters import IngredientSearchFilter, RecipeFilter
from .serializers import (CreateCustomUserSerializer, CreateRecipeSerializer,
                          CustomUserSerializer, GetRecipeSerializer,
                          IngredientSerializer, SubscriptionSerializer,
                          TagSerializer, UniversalRecipeSerializer)


class CreateListRetrieveViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CustomUserViewSet(CreateListRetrieveViewSet):
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return CustomUserSerializer
        return CreateCustomUserSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated]
            return [permission() for permission in permission_classes]
        return super().get_permissions()

    @action(
        methods=('get',),
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        me_profile = self.request.user
        context = {
            'request': request,
        }
        serializer = self.get_serializer(me_profile, context=context)
        return Response(serializer.data)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request, *args, **kwargs):
        user = self.request.user
        subscription = Subscription.objects.filter(users=user)
        paginate = self.paginate_queryset(subscription)
        context = {'request': request}
        serializer = SubscriptionSerializer(
            paginate, context=context, many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('post',),
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, *args, **kwargs):
        instance = self.get_object()
        author = get_object_or_404(CustomUser, id=instance.id)
        user = self.request.user
        subscribe = Subscription.objects.filter(users=user, authors=author)
        if subscribe.exists() or author == user:
            return Response(
                {'errors': 'string'}, status=status.HTTP_400_BAD_REQUEST
            )
        subscribe.create(users=user, authors=author)
        new_subs = subscribe.get(users=user, authors=author)
        serializer = SubscriptionSerializer(new_subs,
                                            context={'request': request})
        return Response(
            data=serializer.data, status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def subscribe_delete(self, request, *args, **kwargs):
        instance = self.get_object()
        author = get_object_or_404(CustomUser, id=instance.id)
        user = self.request.user
        subscribe = Subscription.objects.filter(users=user, authors=author)
        if subscribe.exists():
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'string'}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def set_password(request):
    context = {'request': request}
    serializer = settings.SERIALIZERS.set_password(
        data=request.data, context=context
    )
    serializer.is_valid(raise_exception=True)
    new_password = serializer.validated_data.get('new_password')
    user = CustomUser.objects.get(username=request.user)
    user.set_password(new_password)
    user.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ['name']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return GetRecipeSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user
        author = instance.author
        if user == author:
            return self.update(request, *args, **kwargs)
        detail = 'У вас недостаточно прав для выполнения данного действия.'
        return Response(
            data={'detail': detail}, status=status.HTTP_403_FORBIDDEN
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user
        author = instance.author
        if user == author:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        detail = 'У вас недостаточно прав для выполнения данного действия.'
        return Response(
            data={'detail': detail}, status=status.HTTP_403_FORBIDDEN
        )

    @action(
        methods=('get',),
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        user = self.request.user
        cart_data = Cart.objects.filter(users=user)
        text = '-----------------------Корзина------------------------'
        for cart in cart_data:
            recipe = Recipe.objects.get(id=cart.recipes.pk)
            text += f'\nНазвание рецепта: {recipe.name}'
            ingr_data = RecipeIngredient.objects.filter(recipes=recipe)
            for ingr in ingr_data:
                ingredient = ingr.ingredients.name
                measurement_unit = ingr.ingredients.measurement_unit
                amount = ingr.amount
                text += f'\n - {ingredient}, {measurement_unit} - {amount}'
            text += '\n------------------------------------------------------'
        file = StringIO(text)
        response = HttpResponse(file, content_type='text/plain; charset=utf8')
        return response

    @action(
        methods=('post',),
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
    )
    def shopping_cart(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user
        cart = Cart.objects.filter(users=user, recipes=instance)
        if cart.exists():
            return Response(
                {'errors': 'string'}, status=status.HTTP_400_BAD_REQUEST
            )
        cart.create(users=user, recipes=instance)
        serializer = UniversalRecipeSerializer(
            instance, context={'request': request}
        )
        return Response(
            data=serializer.data, status=status.HTTP_201_CREATED
        )

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user
        cart = Cart.objects.filter(users=user, recipes=instance)
        if cart.exists():
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'string'}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=('post',),
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user

        favorite = Favorite.objects.filter(users=user, recipes=instance)
        if favorite.exists():
            return Response(
                {'errors': 'string'}, status=status.HTTP_400_BAD_REQUEST
            )
        favorite.create(users=user, recipes=instance)
        serializer = UniversalRecipeSerializer(
            instance, context={'request': request}
        )
        return Response(
            data=serializer.data, status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def favorite_delete(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user
        favorite = Favorite.objects.filter(users=user, recipes=instance)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'string'}, status=status.HTTP_400_BAD_REQUEST
        )
