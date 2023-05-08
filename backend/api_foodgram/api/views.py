from io import StringIO

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Subscription,
    Tag,
)

from .filters import RecipeFilter
from .serializers import (
    CcreateCustomUserSerializer,
    CreateRecipeSerializer,
    CustomUserSerializer,
    CustomUserSetPasswordSerializer,
    GetRecipeSerializer,
    IngredientSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UniversalRecipeSerializer,
)

User = get_user_model()


class CreateListRetrieveViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CustomUserViewSet(CreateListRetrieveViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return CustomUserSerializer
        return CcreateCustomUserSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            permission_classes = [permissions.IsAuthenticated]
            return [permission() for permission in permission_classes]
        return super().get_permissions()

    def list(self, request):
        queryset = self.get_queryset()
        context = {
            "request": request,
        }
        paginate = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginate, context=context, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        me_user = self.request.user
        if "me" == pk:
            context = {
                "request": request,
            }
            serializer = self.get_serializer(me_user, context=context)
            return Response(serializer.data)

        user = get_object_or_404(User, id=pk)
        context = {
            "request": request,
        }
        serializer = self.get_serializer(user, context=context)
        return Response(serializer.data)

    @action(
        methods=("get",),
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        url_path="subscriptions",
        url_name="subscriptions",
    )
    def subscriptions(self, request, *args, **kwargs):
        user = self.request.user
        subscription = Subscription.objects.filter(users=user)
        paginate = self.paginate_queryset(subscription)
        context = {"request": request}
        serializer = SubscriptionSerializer(
            paginate, context=context, many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=("post", "delete"),
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
        url_path="subscribe",
        url_name="subscribe",
    )
    def subscribe(self, request, *args, **kwargs):
        instance = self.get_object()
        author = get_object_or_404(User, id=instance.id)
        user = self.request.user

        if self.request.method == "POST":
            subscribe = Subscription.objects.filter(users=user, authors=author)
            if subscribe.exists() or author == user:
                return Response(
                    {"errors": "string"}, status=status.HTTP_400_BAD_REQUEST
                )
            subscribe.create(users=user, authors=author)
            new_subs = subscribe.get(users=user, authors=author)
            serializer = SubscriptionSerializer(new_subs,
                                                context={"request": request})
            return Response(
                data=serializer.data, status=status.HTTP_201_CREATED
            )

        if self.request.method == "DELETE":
            subscribe = Subscription.objects.filter(users=user, authors=author)
            if subscribe.exists():
                subscribe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "string"}, status=status.HTTP_400_BAD_REQUEST
            )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def set_password_profile(request):
    serializer = CustomUserSetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    current_password = serializer.validated_data.get("current_password")
    new_password = serializer.validated_data.get("new_password")
    user = User.objects.get(username=request.user)

    if user.check_password(current_password):
        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        {"password": ["error"]}, status=status.HTTP_400_BAD_REQUEST
    )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


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
        detail = "У вас недостаточно прав для выполнения данного действия."
        return Response(
            data={"detail": detail}, status=status.HTTP_403_FORBIDDEN
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user
        author = instance.author
        if user == author:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        detail = "У вас недостаточно прав для выполнения данного действия."
        return Response(
            data={"detail": detail}, status=status.HTTP_403_FORBIDDEN
        )

    @action(
        methods=("get",),
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        url_path="download_shopping_cart",
        url_name="download_shopping_cart",
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        user = self.request.user
        cart_data = Cart.objects.filter(users=user)
        text = "-----------------------Корзина------------------------"
        for cart in cart_data:
            recipe = Recipe.objects.get(id=cart.recipes.pk)
            text += f"\nНазвание рецепта: {recipe.name}"
            ingr_data = RecipeIngredient.objects.filter(recipes=recipe)
            for ingr in ingr_data:
                ingredient = ingr.ingredients.name
                measurement_unit = ingr.ingredients.measurement_unit
                amount = ingr.amount
                text += f"\n - {ingredient}, {measurement_unit} - {amount}"
            text += "\n------------------------------------------------------"
        file = StringIO(text)
        response = HttpResponse(file, content_type="text/plain; charset=utf8")
        return response

    @action(
        methods=("post", "delete"),
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
        url_path="shopping_cart",
        url_name="shopping_cart",
    )
    def shopping_cart(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user
        if self.request.method == "POST":
            cart = Cart.objects.filter(users=user, recipes=instance)
            if cart.exists():
                return Response(
                    {"errors": "string"}, status=status.HTTP_400_BAD_REQUEST
                )
            cart.create(users=user, recipes=instance)
            serializer = UniversalRecipeSerializer(
                instance, context={"request": request}
            )
            return Response(
                data=serializer.data, status=status.HTTP_201_CREATED
            )

        if self.request.method == "DELETE":
            cart = Cart.objects.filter(users=user, recipes=instance)
            if cart.exists():
                cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "string"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=("post", "delete"),
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
        url_path="favorite",
        url_name="favorite",
    )
    def favorite(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user
        if self.request.method == "POST":
            favorite = Favorite.objects.filter(users=user, recipes=instance)
            if favorite.exists():
                return Response(
                    {"errors": "string"}, status=status.HTTP_400_BAD_REQUEST
                )
            favorite.create(users=user, recipes=instance)
            serializer = UniversalRecipeSerializer(
                instance, context={"request": request}
            )
            return Response(
                data=serializer.data, status=status.HTTP_201_CREATED
            )

        if self.request.method == "DELETE":
            favorite = Favorite.objects.filter(users=user, recipes=instance)
            if favorite.exists():
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "string"}, status=status.HTTP_400_BAD_REQUEST
            )
