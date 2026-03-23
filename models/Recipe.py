from models.DietaryTag import DietaryTag
from models.NutritionalInformation import NutritionalInformation

class Recipe:
    def __init__(
        self,
        name: str,
        ingredients: dict[str, int],
        nutritional_info: NutritionalInformation,
        dietary_tags: list[DietaryTag],
    ):
        """
        The `Recipe` class represents a recipe with its required ingredients and dietary properties

        :param name: display name of the recipe
        :type name: str
        :param ingredients: mapping of ingredient name to number of units required
        :type ingredients: dict[str, int]
        :param nutritional_info: approximate nutritional values per serving
        :type nutritional_info: NutritionalInformation
        :param dietary_tags: list of dietary compliance tags
        :type dietary_tags: list[DietaryTag]
        """
        
        self.name = name
        self.ingredients = ingredients
        self.nutritional_info = nutritional_info
        self.dietary_tags = dietary_tags

        self.is_vegan = DietaryTag.VEGAN in dietary_tags
        self.is_vegetarian = DietaryTag.VEGETARIAN in dietary_tags or self.is_vegan
        self.is_gluten_free = DietaryTag.GLUTEN_FREE in dietary_tags
        self.is_lactose_free = DietaryTag.LACTOSE_FREE in dietary_tags