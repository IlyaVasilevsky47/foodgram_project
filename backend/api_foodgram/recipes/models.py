from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название тега", unique=True, max_length=200
    )
    color = ColorField(verbose_name="Цвет", unique=True, max_length=7)
    slug = models.SlugField(verbose_name="Cлаг", unique=True, max_length=200)

    def __str__(self):
        return self.slug

    class Meta:
        ordering = ("id",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название ингредиента", max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения", max_length=200
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_ingredient',
                fields=['name', 'measurement_unit'],
            )
        ]
        ordering = ("id",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        through="RecipeTag",
        related_name="recipes_tags",
        verbose_name="Теги",
    )
    author = models.ForeignKey(
        User,
        related_name="recipes_author",
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes_ingredients",
        verbose_name="Ингредиенты",
    )
    name = models.CharField(verbose_name="Название рецепта", max_length=200)
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="recipes/images/",
    )
    text = models.TextField(verbose_name="Описание")
    cooking_time = models.PositiveBigIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="Время готовки",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_recipe',
                fields=['name', 'author'],
            )
        ]
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"


class RecipeIngredient(models.Model):
    recipes = models.ForeignKey(
        Recipe,
        related_name="recipeingredient_recipe",
        on_delete=models.CASCADE,
        verbose_name="Рецеты",
    )
    ingredients = models.ForeignKey(
        Ingredient,
        related_name="recipeingredient_ingredient",
        on_delete=models.CASCADE,
        verbose_name="Ингредиенты",
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="Сумма",
    )

    def __str__(self):
        return f"{self.ingredients}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_recipe_ingredient',
                fields=['recipes', 'ingredients'],
            )
        ]
        ordering = ("id",)
        verbose_name = "РецептИнгредиент"
        verbose_name_plural = "РецептыИнгредиенты"


class RecipeTag(models.Model):
    recipes = models.ForeignKey(
        Recipe,
        related_name="tecipetag_recipe",
        on_delete=models.CASCADE,
        verbose_name="Рецеты",
    )
    tags = models.ForeignKey(
        Tag,
        related_name="recipetag_tag",
        on_delete=models.CASCADE,
        verbose_name="Теги",
    )

    def __str__(self):
        return f"{self.tags}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_recipe_tag',
                fields=['recipes', 'tags'],
            )
        ]
        ordering = ("id",)
        verbose_name = "РецептТег"
        verbose_name_plural = "РецептыТеги"


class Actions(models.Model):
    users = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователи",
    )
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепты",
    )

    class Meta:
        abstract = True
        ordering = ("id",)


class Cart(Actions):
    class Meta:
        ordering = ("id",)
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class Favorite(Actions):
    class Meta:
        ordering = ("id",)
        verbose_name = "Избранный"
        verbose_name_plural = "Избранные"


class Subscription(models.Model):
    users = models.ForeignKey(
        User,
        related_name="subscribers",
        on_delete=models.CASCADE,
        verbose_name="Пользователи",
    )
    authors = models.ForeignKey(
        User,
        related_name="subscriptions",
        on_delete=models.CASCADE,
        verbose_name="Аторы",
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
