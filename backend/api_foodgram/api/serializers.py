import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, RecipeTag, Subscription, Tag)
from users.models import CustomUser

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        is_subscribed = Subscription.objects.filter(
            users=request.user.id, authors=author
        )
        return is_subscribed.exists()


class CreateCustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {
            'request': request,
        }
        serializers = CustomUserSerializer(instance, context=context)
        return serializers.data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class CreateRecipeIngredientSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        required=True, validators=[MinValueValidator(1)]
    )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class GetRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    name = serializers.CharField(max_length=200)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipes=obj.id)
        ingredients_data = []
        for ingr in ingredients:
            ingr_info = Ingredient.objects.get(name=ingr.ingredients)
            ingredients_data.append(
                {
                    'id': ingr_info.pk,
                    'name': ingr_info.name,
                    'measurement_unit': ingr_info.measurement_unit,
                    'amount': ingr.amount,
                }
            )
        return ingredients_data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        is_favorited = Favorite.objects.filter(users=request.user.id,
                                               recipes=obj)
        return is_favorited.exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        is_in_shopping_cart = Cart.objects.filter(users=request.user.id,
                                                  recipes=obj)
        return is_in_shopping_cart.exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = CreateRecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    name = serializers.CharField(
        max_length=200,
        validators=[UniqueValidator(queryset=Recipe.objects.all())]
    )

    class Meta:
        model = Recipe
        read_only_fields = ('author',)
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for tags in tags_data:
            RecipeTag.objects.create(recipes=recipe, tags=tags)

        ingredients_list = []
        for ingredients in ingredients_data:
            ingredients_list.append(RecipeIngredient(
                recipes=recipe,
                ingredients=ingredients['id'],
                amount=ingredients['amount']
            ))
        RecipeIngredient.objects.bulk_create(ingredients_list)

        return recipe

    def validate(self, data):
        ingredients_data = data['ingredients']
        old_ingredient = None
        for ingredients in ingredients_data:
            new_ingredient = ingredients['id']
            if new_ingredient == old_ingredient:
                raise serializers.ValidationError(
                    {'ingredients': {'id': 'Повторяется ингредиент'}}
                )
            old_ingredient = new_ingredient

        tags_data = data['tags']
        old_tags = None
        for tags in tags_data:
            new_tags = tags
            if new_tags == old_tags:
                raise serializers.ValidationError({'tags': 'Повторяется тег'})
            old_tags = new_tags

        return data

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            data = []

            for ingredient in ingredients_data:
                ingr = RecipeIngredient.objects.filter(
                    recipes=instance,
                    ingredients=ingredient['id'],
                )
                if ingr.exists():
                    ingr.update(amount=ingredient['amount'])
                else:
                    ingr.create(
                        recipes=instance,
                        ingredients=ingredient['id'],
                        amount=ingredient['amount']
                    )
                data.append(ingredient['id'])
            instance.ingredients.set(data)

        if 'tags' in validated_data:
            tags_data = validated_data.get('tags')
            data = []
            for tag in tags_data:
                RecipeTag.objects.get_or_create(recipes=instance, tags=tag)
                data.append(tag.id)
            instance.tags.set(data)
        instance.save()
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {
            'request': request,
        }
        serializers = GetRecipeSerializer(instance, context=context)
        return serializers.data


class UniversalRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.CharField(
        source='authors.email'
    )
    id = serializers.IntegerField(source='authors.id')
    username = serializers.CharField(
        source='authors.username'
    )
    first_name = serializers.CharField(
        source='authors.first_name'
    )
    last_name = serializers.CharField(
        source='authors.last_name'
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        subscription = Subscription.objects.filter(users=obj.users,
                                                   authors=obj.authors)
        return subscription.exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.authors)
        request = self.context.get('request')
        recipes_data = []
        for recipe in recipes:
            image = request.build_absolute_uri(recipe.image.url)
            recipes_data.append(
                {
                    'id': recipe.id,
                    'name': recipe.name,
                    'image': image,
                    'cooking_time': recipe.cooking_time,
                }
            )
        return recipes_data

    def get_recipes_count(self, obj):
        recipes = Recipe.objects.filter(author=obj.authors)
        return recipes.count()
