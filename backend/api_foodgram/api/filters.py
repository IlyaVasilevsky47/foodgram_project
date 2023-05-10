from django_filters import rest_framework
from rest_framework import filters

from recipes.models import Cart, Favorite, Recipe, Tag


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'


class RecipeFilter(rest_framework.FilterSet):
    is_favorited = rest_framework.BooleanFilter(
        field_name='favorited', method='filter_favorited', label='Изброное'
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(
        field_name='shopping_cart',
        method='filter_shopping_cart',
        label='Корзина'
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        label='Теги',
    )

    def filter_favorited(self, queryset, name, value):
        user = self.request.user
        favorite_data = Favorite.objects.filter(users=user.id)
        pk_data = []
        for favorite in favorite_data:
            pk_data.append(favorite.recipes.pk)
        return queryset.filter(pk__in=pk_data)

    def filter_shopping_cart(self, queryset, name, value):
        user = self.request.user
        сart_data = Cart.objects.filter(users=user.id)
        pk_data = []
        for сart in сart_data:
            pk_data.append(сart.recipes.pk)
        return queryset.filter(pk__in=pk_data)

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'tags', 'author')
