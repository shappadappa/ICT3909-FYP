class UserPreferences:
    def __init__(
        self,
        weekly_budget: float = 50.0,
        calorie_target_per_day: float = 2500.0,
        protein_target_per_day: float = 50.0,
        is_vegetarian: bool = False,
        is_vegan: bool = False,
        requires_gluten_free: bool = False,
        requires_lactose_free: bool = False,
    ):
        """
        The 'UserPreferences' class captures user dietary constraints and budget for use in the fitness function

        :param weekly_budget: maximum spend on groceries for the week in EUR (default = 50)
        :type weekly_budget: float
        :param calorie_target_per_day: target caloric intake per day (default = 2500)
        :type calorie_target_per_day: float
        :param protein_target_per_day: target protein intake per day (default = 50)
        :type protein_target_per_day: float
        :param is_vegetarian: if the user requires vegetarian meals (default = False)
        :type is_vegetarian: bool
        :param is_vegan: if the user requires vegan meals (default = False, but if True then is_vegetarian will also be set to True)
        :type is_vegan: bool
        :param requires_gluten_free: if the user requires gluten-free meals (gluten intolerant or celiac) (default = False)
        :type requires_gluten_free: bool
        :param requires_lactose_free: if the user requires lactose-free meals (lactose intolerant) (default = False)
        :type requires_lactose_free: bool
        """

        assert weekly_budget >= 0, "Weekly budget must be non-negative"
        assert calorie_target_per_day > 0, "Calorie target per day must be positive"
        assert not (is_vegan and not is_vegetarian), "Cannot be vegan without being vegetarian"

        self.weekly_budget = weekly_budget
        self.calorie_target_per_day = calorie_target_per_day
        self.protein_target_per_day = protein_target_per_day
        self.is_vegetarian = is_vegetarian or is_vegan
        self.is_vegan = is_vegan
        self.requires_gluten_free = requires_gluten_free
        self.requires_lactose_free = requires_lactose_free

    def to_dict(self) -> dict:
        """
        Converts the user preferences to a dictionary format

        :return: dictionary representation of the user preferences
        :rtype: dict
        """

        return {
            "weekly_budget": self.weekly_budget,
            "calorie_target_per_day": self.calorie_target_per_day,
            "protein_target_per_day": self.protein_target_per_day,
            "is_vegetarian": self.is_vegetarian,
            "is_vegan": self.is_vegan,
            "requires_gluten_free": self.requires_gluten_free,
            "requires_lactose_free": self.requires_lactose_free,
        }
