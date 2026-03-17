class NutritionalInformation:
    def __init__(self, 
                 calories: float, 
                 carbohydrates: float, 
                 sugar: float, 
                 protein: float, 
                 fat: float, 
                 saturated_fat: float, 
                 fiber: float, 
                 sodium: float, 
                 is_gluten_free: bool, 
                 is_lactose_free: bool, 
                 is_vegetarian: bool,
                 is_vegan: bool,
                 ):
        """
        The 'NutritionalInformation' class, represents the nutritional information of an ingredient, useful for recipe suggestions and dietary management. All listed attributes are per 100 grams of the ingredient

        :param calories: number of calories in the ingredient
        :type calories: float
        :param carbohydrates: amount of carbohydrates in grams
        :type carbohydrates: float
        :param sugar: amount of sugar in grams
        :type sugar: float
        :param protein: amount of protein in grams
        :type protein: float
        :param fat: amount of fat in grams
        :type fat: float
        :param saturated_fat: amount of saturated fat in grams
        :type saturated_fat: float
        :param fiber: amount of fiber in grams
        :type fiber: float
        :param sodium: amount of sodium in milligrams
        :type sodium: float
        :param is_gluten_free: whether the ingredient is gluten free
        :type is_gluten_free: bool
        :param is_lactose_free: whether the ingredient is lactose free
        :type is_lactose_free: bool
        :param is_vegetarian: whether the ingredient is vegetarian
        :type is_vegetarian: bool
        :param is_vegan: whether the ingredient is vegan
        :type is_vegan: bool
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

