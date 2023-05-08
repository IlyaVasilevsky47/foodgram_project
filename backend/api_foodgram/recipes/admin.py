from django.contrib import admin

from .models import (
    Cart,
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    Subscription,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "color",
        "slug",
    )
    list_filter = ("name",)
    search_fields = ("name",)
    empty_value_display = "-пусто-"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "measurement_unit",
    )
    list_filter = ("name",)
    search_fields = ("name",)
    empty_value_display = "-пусто-"


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "author",
        "image",
        "text",
        "cooking_time",
        "quantity_in_favorites",
    )
    list_filter = ("name", "author__username", "tags")
    search_fields = ("name", "author__username", "tags")
    inlines = [RecipeIngredientInline, RecipeTagInline]
    empty_value_display = "-пусто-"

    def quantity_in_favorites(self, obj):
        result = Favorite.objects.filter(recipes=obj)
        return result.count()

    quantity_in_favorites.short_description = "Количевство в  избраном"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        "recipes",
        "ingredients",
        "amount",
    )
    list_filter = ("recipes__name", "ingredients__name")
    search_fields = ("recipes__name", "ingredients__name")
    empty_value_display = "-пусто-"


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = (
        "recipes",
        "tags",
    )
    list_filter = ("recipes__name", "tags__name")
    search_fields = ("recipes__name", "tags__name")
    empty_value_display = "-пусто-"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "users",
        "recipes",
    )
    list_filter = ("users__username", "recipes__author")
    search_fields = ("users__username", "recipes__author")
    empty_value_display = "-пусто-"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "users",
        "recipes",
    )
    list_filter = ("users__username", "recipes__author")
    search_fields = ("users__username", "recipes__author")
    empty_value_display = "-пусто-"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "users",
        "authors",
    )
    list_filter = ("users__username", "authors__username")
    search_fields = ("users__username", "authors__username")
    empty_value_display = "-пусто-"
