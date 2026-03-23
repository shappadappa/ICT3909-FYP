from models.NutritionalInformation import NutritionalInformation

from datetime import datetime

class Ingredient:
    def __init__(self, name: str, quantity: int, nutritional_info: NutritionalInformation, estimated_expiration_date: datetime, estimated_financial_cost: float):
        """
        `Ingredient` class represents an ingredient in the pantry with various attributes useful for recipe suggestions and inventory management

        :param name: name of the ingredient
        :type name: str
        :param quantity: quantity of the ingredient in stock
        :type quantity: int
        :param nutritional_info: nutritional information of the ingredient
        :type nutritional_info: NutritionalInformation
        :param estimated_expiration_date: estimated expiration date of the ingredient
        :type estimated_expiration_date: datetime
        :param estimated_financial_cost: estimated financial cost of the ingredient
        :type estimated_financial_cost: float
        """

        self.name = name
        self.quantity = quantity
        self.nutritional_info = nutritional_info
        self.estimated_expiration_date = estimated_expiration_date
        self.estimated_financial_cost = estimated_financial_cost

    def add(self, amount: int = 1):
        """
        Adds a specified amount to the ingredient's quantity
        
        :param amount: amount to add to the ingredient's quantity (default = 1)
        :type amount: int
        """

        self.quantity += amount

    def remove(self, amount: int = 1):
        """
        Removes a specified amount from the ingredient's quantity
        
        :param amount: amount to remove from the ingredient's quantity (default = 1)
        :type amount: int
        """

        self.quantity -= amount

    def is_expired(self, current_date: datetime | None = None) -> bool:
        """
        Checks if the ingredient is expired based on the current date and the estimated expiration date

        :param current_date: current date to compare with the estimated expiration date (default = None, uses current system date)
        :type current_date: datetime | None

        :return: True if the ingredient is expired, False otherwise
        :rtype: bool
        """

        if current_date is None:
            current_date = datetime.now()

        current_date_ms = current_date.timestamp()

        expiration_date_ms = self.estimated_expiration_date.timestamp()

        return current_date_ms > expiration_date_ms