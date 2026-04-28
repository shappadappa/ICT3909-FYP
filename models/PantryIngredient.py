from datetime import datetime

from models.Ingredient import Ingredient
from models.NutritionalInformation import NutritionalInformation


class PantryIngredient(Ingredient):
    def __init__(
        self,
        name: str,
        nutritional_information: NutritionalInformation,
        estimated_expiration_date: datetime = datetime(9999, 12, 31),
    ):
        """
        `PantryIngredient` class extends `Ingredient` with additional attributes specific to ingredients stored in the pantry, such as estimated expiration date

        :param name: name of the ingredients
        :type name: str
        :param nutritional_information: nutritional information of the ingredient per 100 grams
        :type nutritional_information: NutritionalInformation
        :param estimated_expiration_date: estimated expiration date of the ingredient (default = datetime(9999, 12, 31), meaning it does not expire)
        :type estimated_expiration_date: datetime
        """

        super().__init__(name, nutritional_information)

        self.estimated_expiration_date = estimated_expiration_date

    def is_expired(self, current_date: datetime | None = None) -> bool:
        """
        Checks if the ingredient is expired based on the current date and the estimated expiration date

        :param current_date: current date to compare with the estimated expiration date (default = None, uses current system date)
        :type current_date: datetime | None

        :return: True if the ingredient is expired, False otherwise
        :rtype: bool
        """

        if self.estimated_expiration_date is None:
            return False

        if current_date is None:
            current_date = datetime.now()

        return current_date.timestamp() > self.estimated_expiration_date.timestamp()

    def print(self):
        """
        Prints a summary of the ingredient's details
        """

        expiry_str = self.estimated_expiration_date.strftime("%Y-%m-%d") if self.estimated_expiration_date else "N/A"

        print(f"Ingredient: {self.name}\n\tEstimated Expiration Date: {expiry_str}\n\tNutritional Information:")

        self.nutritional_information.print(2)
