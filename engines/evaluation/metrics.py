from datetime import datetime

from models import Pantry, Recipe, UserPreferences


def get_ingredient_utilisation_score(meal_plan: list[list[Recipe]], pantry: Pantry) -> float:
    """
    Calculates the ingredient utilisation score for a given meal plan and pantry

    :param meal_plan: a list of lists of Recipe objects representing the meal plan
    :type meal_plan: list[list[Recipe]]
    :param pantry: a Pantry object representing the available ingredients
    :type pantry: Pantry

    :return: the ingredient utilisation score as a float between 0 and 1
    :rtype: float
    """

    pantry_stock = pantry.stock
    consumed_stock: dict[str, float] = dict.fromkeys(pantry_stock.keys(), 0.0)

    for day_meals in meal_plan:
        for recipe in day_meals:
            for ingredient_name, quantity_needed in recipe.ingredients.items():
                available = pantry_stock.get(ingredient_name, 0.0) - consumed_stock.get(ingredient_name, 0.0)
                from_pantry = max(0.0, min(available, quantity_needed))
                consumed_stock[ingredient_name] = consumed_stock.get(ingredient_name, 0.0) + from_pantry

    total_available = sum(pantry_stock.values())
    if total_available == 0:
        return 0.0

    total_consumed = sum(consumed_stock.values())
    return total_consumed / total_available


def get_expiry_weighted_utilisation_score(
    meal_plan: list[list[Recipe]], pantry: Pantry, current_date: datetime
) -> float:
    """
    Calculates the expiry-weighted utilisation score for a given meal plan and pantry.
    Ingredients closer to expiry contribute more weight when consumed:
        score = Σ quantity_used * (1 / days_to_expiry)

    :param meal_plan: a list of lists of Recipe objects representing the meal plan
    :type meal_plan: list[list[Recipe]]
    :param pantry: a Pantry object representing the available ingredients
    :type pantry: Pantry

    :return: the expiry-weighted utilisation score (higher is better)
    :rtype: float
    """

    pantry_stock = pantry.stock
    days_until_expiry = pantry.get_days_until_expiry(current_date)
    consumed_stock: dict[str, float] = dict.fromkeys(pantry_stock.keys(), 0.0)

    for day_meals in meal_plan:
        for recipe in day_meals:
            for ingredient_name, quantity_needed in recipe.ingredients.items():
                available = pantry_stock.get(ingredient_name, 0.0) - consumed_stock.get(ingredient_name, 0.0)
                from_pantry = max(0.0, min(available, quantity_needed))
                consumed_stock[ingredient_name] = consumed_stock.get(ingredient_name, 0.0) + from_pantry

    score = 0.0
    for ingredient_name, quantity_used in consumed_stock.items():
        if quantity_used == 0.0:
            continue

        days = max(days_until_expiry.get(ingredient_name, 1), 1)
        score += quantity_used * (1.0 / days)

    return score


def dietary_compliance(meal_plan: list[list[Recipe]], user_preferences: UserPreferences) -> float:
    """
    Calculates the dietary compliance score for a given meal plan and user preferences

    Hard constraints (vegan, vegetarian, gluten-free, lactose-free) are checked first. Any violation immediately returns 0.0. Otherwise, the score reflects how closely daily calorie and protein totals match the user's targets, using mean relative error

    :param meal_plan: a list of lists of Recipe objects representing the meal plan
    :type meal_plan: list[list[Recipe]]
    :param user_preferences: the user's dietary preferences and nutritional targets
    :type user_preferences: UserPreferences

    :return: dietary compliance score as a float between 0 and 1
    :rtype: float
    """

    for day_meals in meal_plan:
        for recipe in day_meals:
            if (
                (user_preferences.is_vegan and not recipe.is_vegan)
                or (user_preferences.is_vegetarian and not recipe.is_vegetarian)
                or (user_preferences.requires_gluten_free and not recipe.is_gluten_free)
                or (user_preferences.requires_lactose_free and not recipe.is_lactose_free)
            ):
                return 0.0

    total_relative_error = 0.0
    num_days = len(meal_plan)

    for day_meals in meal_plan:
        daily_calories = sum(recipe.nutritional_information.get_nutritional_value("calories") for recipe in day_meals)
        daily_protein = sum(recipe.nutritional_information.get_nutritional_value("protein") for recipe in day_meals)

        if user_preferences.calorie_target_per_day > 0:
            total_relative_error += (
                abs(daily_calories - user_preferences.calorie_target_per_day) / user_preferences.calorie_target_per_day
            )
        if user_preferences.protein_target_per_day > 0:
            total_relative_error += (
                abs(daily_protein - user_preferences.protein_target_per_day) / user_preferences.protein_target_per_day
            )

    mean_relative_error = total_relative_error / (num_days * 2)
    return max(0.0, 1.0 - mean_relative_error)
