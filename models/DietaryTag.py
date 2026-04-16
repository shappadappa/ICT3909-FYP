from enum import Enum, auto


class DietaryTag(Enum):
    """
    `DietaryTag` is an Enum representing various dietary compliance tags that can be associated with recipes and ingredients, categorising recipes based on dietary restrictions and preferences
    """

    VEGETARIAN = auto()
    VEGAN = auto()
    GLUTEN_FREE = auto()
    LACTOSE_FREE = auto()
