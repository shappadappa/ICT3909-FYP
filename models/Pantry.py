from models.Ingredient import Ingredient

class Pantry:
    def __init__(self):
        """
        The `Pantry` class represents a collection of ingredients and their available quantities
        """

        self._ingredients: dict[str, Ingredient] = {}
        self._quantities: dict[str, int] = {}

    @property
    def ingredients(self) -> list[Ingredient]:
        """
        Returns the list of unique ingredient objects currently in the pantry
        
        :return: list of unique ingredient objects currently in the pantry
        :rtype: list[Ingredient]
        """

        return list(self._ingredients.values())

    @property
    def stock(self) -> dict[str, int]:
        """
        Returns a snapshot of ingredient name to available quantity

        :return: dictionary mapping ingredient names to their available quantities
        :rtype: dict[str, int]
        """

        return dict(self._quantities)

    def add(self, ingredient: Ingredient, quantity: int):
        """
        Adds a quantity of an ingredient to the pantry. If the ingredient already exists,
        its quantity is increased.

        :param ingredient: ingredient to add
        :type ingredient: Ingredient
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
            print(f"Quantity: {qty}")
            ingredient.print()
            print("---")
