import io
import logging
from csv import DictReader

from django.core.management import BaseCommand

from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    Subscription,
    Tag,
)
from users.models import CustomUser

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the child data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):
    help = "Loads data from children.csv"

    def handle_1(self, *args, **options):
        logging.info("First part")
        if Ingredient.objects.exists():
            logging.warning("child data already loaded...exiting.")
            raise Exception(ALREDY_LOADED_ERROR_MESSAGE)

        logging.info("Loading - data a table - Ingredient")
        for row in DictReader(
            io.open("static/data/ingredients.csv", mode="r", encoding="utf-8")
        ):
            name = row["name"]
            measurement_unit = row["measurement_unit"]
            Ingredient.objects.get_or_create(
                name=name, measurement_unit=measurement_unit
            )
        logging.info("Successfully - loading data table - Ingredient")

        logging.info("Further")

        logging.info("Loading - data a table - Tag")
        for row in DictReader(
            io.open("static/data/tag.csv", mode="r", encoding="utf-8")
        ):
            name = str(row["name"])
            color = str(row["color"])
            slug = str(row["slug"])
            Tag.objects.get_or_create(name=name, color=color, slug=slug)
        logging.info("Successfully - loading data table - Tag")

        logging.info("Further")

        logging.info("Loading - data a table - CustomUser")
        for row in DictReader(
            io.open("static/data/customuser.csv", mode="r", encoding="utf-8")
        ):
            password = row["password"]
            email = row["email"]
            username = row["username"]
            first_name = row["first_name"]
            last_name = row["last_name"]
            CustomUser.objects.get_or_create(
                password=password,
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
        logging.info("Successfully - loading data table - CustomUser")

        logging.info("Further")

        logging.info("Loading - data a table - Recipe")
        for row in DictReader(
            io.open("static/data/recipe.csv", mode="r", encoding="utf-8")
        ):
            author = CustomUser.objects.get(pk=row["author"])
            name = row["name"]
            image = row["image"]
            text = row["text"]
            cooking_time = row["cooking_time"]
            Recipe.objects.get_or_create(
                author=author,
                name=name,
                image=image,
                text=text,
                cooking_time=cooking_time,
            )
        logging.info("Successfully - loading data table - Recipe")

        logging.info("Further")

        logging.info("Loading - data a table - RecipeTag")
        for row in DictReader(
            io.open("static/data/recipetag.csv", mode="r", encoding="utf-8")
        ):
            recipes = Recipe.objects.get(pk=row["recipes"])
            tags = Tag.objects.get(pk=row["tags"])
            RecipeTag.objects.get_or_create(
                recipes=recipes,
                tags=tags,
            )
        logging.info("Successfully - loading data table - RecipeTag")

        logging.info("Further")

        logging.info("Loading - data a table - RecipeIngredient")
        for row in DictReader(
            io.open(
                "static/data/recipeingredient.csv",
                mode="r",
                encoding="utf-8"
            )
        ):
            recipes = Recipe.objects.get(pk=row["recipes"])
            ingredients = Ingredient.objects.get(pk=row["ingredients"])
            amount = row["amount"]
            RecipeIngredient.objects.get_or_create(
                recipes=recipes,
                ingredients=ingredients,
                amount=amount,
            )
        logging.info("Successfully - loading data table - RecipeIngredient")

    def handle_2(self, *args, **options):
        logging.info("Further second part")
        logging.info("Loading - data a table - Subscription")
        for row in DictReader(
            io.open("static/data/subscription.csv", mode="r", encoding="utf-8")
        ):
            users = CustomUser.objects.get(pk=row["users"])
            authors = CustomUser.objects.get(pk=row["authors"])
            Subscription.objects.get_or_create(
                users=users,
                authors=authors,
            )
        logging.info("Successfully - loading data table - Subscription")

        logging.info("Further")

        logging.info("Loading - data a table - Favorite")
        for row in DictReader(
            io.open("static/data/favorite.csv", mode="r", encoding="utf-8")
        ):
            users = CustomUser.objects.get(pk=row["users"])
            recipes = Recipe.objects.get(pk=row["recipes"])
            Favorite.objects.get_or_create(
                users=users,
                recipes=recipes,
            )
        logging.info("Successfully - loading data table - Favorite")

        logging.info("Further")

        logging.info("Loading - data a table - Cart")
        for row in DictReader(
            io.open("static/data/cart.csv", mode="r", encoding="utf-8")
        ):
            users = CustomUser.objects.get(pk=row["users"])
            recipes = Recipe.objects.get(pk=row["recipes"])
            Cart.objects.get_or_create(
                users=users,
                recipes=recipes,
            )
        logging.info("Successfully - loading data table - Cart")

        logging.info("Further")

        logging.info("Successfully - all uploaded")
