from models.NutritionalInformation import NutritionalInformation


class Ingredient:
    def __init__(
        self,
        name: str,
        nutritional_information: NutritionalInformation,
    ):
        """
        `Ingredient` class represents an ingredient in the pantry with various attributes useful for recipe suggestions and inventory management

        :param name: name of the ingredient
        :type name: str
        :param nutritional_information: nutritional information of the ingredient per 100 grams
        :type nutritional_information: NutritionalInformation

        """

        self.name = name
        self.nutritional_information = nutritional_information

    def print(self):
        """
        Prints a summary of the ingredient's details
        """

        print(f"Ingredient: {self.name}")
        print("\tNutritional Information per 100g:")

        self.nutritional_information.print(2)

    def to_dict(self) -> dict:
        """
        Converts the ingredient object to a dictionary format

        :return: dictionary representation of the ingredient
        :rtype: dict
        """

        return {"name": self.name, "nutritional_information": self.nutritional_information.to_dict()}
