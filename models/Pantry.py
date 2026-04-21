from datetime import datetime

from models.PantryIngredient import PantryIngredient


class Pantry:
    def __init__(self):
        """
        The `Pantry` class represents a collection of ingredients and their available quantities
        """

        self._ingredients: dict[str, PantryIngredient] = {}
        self._quantities: dict[str, float] = {}

    @property
    def ingredients(self) -> list[PantryIngredient]:
        """
        Returns the list of unique ingredient objects currently in the pantry

        :return: list of unique ingredient objects currently in the pantry
        :rtype: list[PantryIngredient]
        """

        return list(self._ingredients.values())

    @property
    def stock(self) -> dict[str, float]:
        """
        Returns a snapshot of ingredient name to available quantity

        :return: dictionary mapping ingredient names to their available quantities in grams
        :rtype: dict[str, float]
        """

        return dict(self._quantities)

    @property
    def ingredient_costs(self) -> dict[str, float]:
        """
        Returns a snapshot of ingredient name to estimated financial cost per unit

        :return: dictionary mapping ingredient names to their estimated financial cost per unit
        :rtype: dict[str, float]
        """

        return {name: ingredient.estimated_financial_cost for name, ingredient in self._ingredients.items()}

    def get_days_until_expiry(self, current_date: datetime) -> dict[str, int]:
        """
        Returns a snapshot of ingredient name to days until estimated expiration

        :param current_date: current date to compare with the estimated expiration dates
        :type current_date: datetime

        :return: dictionary mapping ingredient names to their estimated days until expiration
        :rtype: dict[str, int]
        """

        return {
            name: max((ingredient.estimated_expiration_date - current_date).days, 0)
            for name, ingredient in self._ingredients.items()
        }

    def add(self, ingredient: PantryIngredient, quantity: int):
        """
        Adds a quantity of an ingredient to the pantry. If the ingredient already exists,
        its quantity is increased.

        :param ingredient: ingredient to add
        :type ingredient: PantryIngredient
        :param quantity: number of units to add
        :type quantity: int
        """

        if ingredient.name in self._ingredients:
            self._quantities[ingredient.name] += quantity
        else:
            self._ingredients[ingredient.name] = ingredient
            self._quantities[ingredient.name] = quantity

    def print(self):
        """
        Prints the details of all ingredients currently in the pantry
        """

        for name, ingredient in self._ingredients.items():
            qty = self._quantities[name]
            print("---")
            print(f"Quantity: {qty} g")
            ingredient.print()
            print("---")
