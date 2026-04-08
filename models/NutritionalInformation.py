class NutritionalInformation:
    def __init__(self, 
                 calories: float | None = None, 
                 carbohydrates: float | None = None, 
                 sugar: float | None = None, 
                 protein: float | None = None, 
                 fat: float | None = None, 
                 saturated_fat: float | None = None, 
                 fiber: float | None = None, 
                 sodium: float | None = None, 
                 is_gluten_free: bool | None = None, 
                 is_lactose_free: bool | None = None, 
                 is_vegetarian: bool | None = None,
                 is_vegan: bool | None = None,
                 ):
        """
        The `NutritionalInformation` class represents the nutritional information of an ingredient or recipe. All listed attributes are dependent on the unit quantity of the ingredient/recipe

        :param calories: number of calories in the ingredient in kcal (default = None)
        :type calories: float | None
        :param carbohydrates: amount of carbohydrates in grams (default = None)
        :type carbohydrates: float | None
        :param sugar: amount of sugar in grams (default = None)
        :type sugar: float | None
        :param protein: amount of protein in grams (default = None)
        :type protein: float | None
        :param fat: amount of fat in grams (default = None)
        :type fat: float | None
        :param saturated_fat: amount of saturated fat in grams (default = None)
        :type saturated_fat: float | None
        :param fiber: amount of fiber in grams (default = None)
        :type fiber: float | None
        :param sodium: amount of sodium in milligrams (default = None)
        :type sodium: float | None
        :param is_gluten_free: whether the ingredient is gluten free (default = None)
        :type is_gluten_free: bool | None
        :param is_lactose_free: whether the ingredient is lactose free (default = None)
        :type is_lactose_free: bool | None
        :param is_vegetarian: whether the ingredient is vegetarian (default = None)
        :type is_vegetarian: bool | None
        :param is_vegan: whether the ingredient is vegan (default = None)
        :type is_vegan: bool | None
        """

        self.calories = calories
        self.carbohydrates = carbohydrates
        self.sugar = sugar
        self.protein = protein
        self.fat = fat
        self.saturated_fat = saturated_fat
        self.fiber = fiber
        self.sodium = sodium
        self.is_gluten_free = is_gluten_free
        self.is_lactose_free = is_lactose_free
        self.is_vegetarian = is_vegetarian
        self.is_vegan = is_vegan

    def print(self, tab_indent: int = 0):
        """
        Prints the nutritional information in a readable format

        :param tab_indent: number of tabs to indent the printed information (default = 0)
        :type tab_indent: int
        """

        indent = "\t" * tab_indent

        print(
            f"{indent}Calories: {self.calories} kcal\n"
            f"{indent}Carbohydrates: {self.carbohydrates} g\n"
            f"{indent}Sugar: {self.sugar} g\n"
            f"{indent}Protein: {self.protein} g\n"
            f"{indent}Fat: {self.fat} g\n"
            f"{indent}Saturated Fat: {self.saturated_fat} g\n"
            f"{indent}Fiber: {self.fiber} g\n"
            f"{indent}Sodium: {self.sodium} mg\n"
            f"{indent}Gluten Free: {'Yes' if self.is_gluten_free else 'No'}\n"
            f"{indent}Lactose Free: {'Yes' if self.is_lactose_free else 'No'}\n"
            f"{indent}Vegetarian: {'Yes' if self.is_vegetarian else 'No'}\n"
            f"{indent}Vegan: {'Yes' if self.is_vegan else 'No'}"
        )

    def get_nutritional_value(self, attribute: str) -> float | bool | None:
        """
        Returns the value of the specified nutritional attribute

        :param attribute: name of the nutritional attribute to retrieve
        :type attribute: str

        :return: value of the specified nutritional attribute, or None if the attribute does not exist
        :rtype: float | bool | None
        """

        if hasattr(self, attribute):
            return getattr(self, attribute)
        else:
            return None
        
    def set_nutritional_value(self, attribute: str, value: float | bool):
        """
        Sets the value of the specified nutritional attribute

        :param attribute: name of the nutritional attribute to set
        :type attribute: str
        :param value: value to set for the specified nutritional attribute
        :type value: float | bool
        """

        if hasattr(self, attribute):
            setattr(self, attribute, value)

    @property
    def keys(self) -> list[str]:
        """
        Returns a list of the keys of the nutritional information attributes

        :return: list of nutritional information attribute keys
        :rtype: list[str]
        """

        return [
            "calories",
            "carbohydrates",
            "sugar",
            "protein",
            "fat",
            "saturated_fat",
            "fiber",
            "sodium",
            "is_gluten_free",
            "is_lactose_free",
            "is_vegetarian",
            "is_vegan"
        ]