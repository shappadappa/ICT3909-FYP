from datetime import datetime

from engines.utils import get_consumed_stock
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

    consumed_stock = get_consumed_stock(meal_plan, pantry_stock)

    total_available = sum(pantry_stock.values())
    if total_available == 0:
        return 0.0

    total_consumed = sum(consumed_stock.values())
    return total_consumed / total_available


def get_expiry_weighted_utilisation_score(
    meal_plan: list[list[Recipe]], pantry: Pantry, current_date: datetime
) -> float:
    """
    Calculates the expiry-weighted utilisation score for a given meal plan and pantry

    Ingredients closer to expiry contribute more weight when consumed. The raw score (sum of quantity_used x 1/days_to_expiry) is normalised by total pantry stock so the result is bounded to [0, 1]

    A score of 1.0 means all stock was consumed and everything expired in exactly 1 day (worst urgency)

    :param meal_plan: a list of lists of Recipe objects representing the meal plan
    :type meal_plan: list[list[Recipe]]
    :param pantry: a Pantry object representing the available ingredients
    :type pantry: Pantry

    :return: the expiry-weighted utilisation score as a float between 0 and 1 (higher is better)
    :rtype: float
    """

    pantry_stock = pantry.stock
    days_until_expiry = pantry.get_days_until_expiry(current_date)

    consumed_stock = get_consumed_stock(meal_plan, pantry_stock)

    total_available = sum(pantry_stock.values())
    if total_available == 0.0:
        return 0.0

    score = 0.0
    for ingredient_name, quantity_used in consumed_stock.items():
        if quantity_used == 0.0:
            continue

        days = max(days_until_expiry.get(ingredient_name, 1), 1)
        score += quantity_used * (1.0 / days)

    return min(score / total_available, 1.0)


def get_expiry_waste_score(meal_plan: list[list[Recipe]], pantry: Pantry, current_date: datetime) -> float:
    """
    Calculates the expiry waste score for a given meal plan and pantry

    Defined as the total grams of pantry stock that will expire within the planning week but are not consumed by the meal plan, divided by total pantry grams available.

    The result is in [0, 1] and lower is better

    :param meal_plan: a list of lists of Recipe objects representing the meal plan
    :type meal_plan: list[list[Recipe]]
    :param pantry: a Pantry object representing the available ingredients
    :type pantry: Pantry
    :param current_date: the current date used to determine days until expiry
    :type current_date: datetime

    :return: expiry waste score as a float between 0 and 1 (lower is better)
    :rtype: float
    """

    pantry_stock = pantry.stock
    total_available = sum(pantry_stock.values())

    if total_available == 0.0:
        return 0.0

    days_until_expiry = pantry.get_days_until_expiry(current_date)
    consumed_stock = get_consumed_stock(meal_plan, pantry_stock)

    expired_unused = 0.0
    for name, available in pantry_stock.items():
        if days_until_expiry.get(name, 999) <= 7:
            consumed = consumed_stock.get(name, 0.0)
            expired_unused += max(0.0, available - consumed)

    return expired_unused / total_available


def get_dietary_compliance(meal_plan: list[list[Recipe]], user_preferences: UserPreferences) -> float:
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


def get_budget_efficiency(
    meal_plan: list[list[Recipe]], pantry: Pantry, ingredient_costs: dict[str, float], weekly_budget: float
) -> float:
    """
    Calculates the budget efficiency score for a given meal plan, pantry, ingredient costs, and weekly budget

    The score is defined as (weekly_budget / total_cost_of_purchased_ingredients), capped at 1.0, since spending less than the budget is better but there's no additional reward for being significantly under budget

    :param meal_plan: a list of lists of Recipe objects representing the meal plan
    :type meal_plan: list[list[Recipe]]
    :param pantry: a Pantry object representing the available ingredients
    :type pantry: Pantry
    :param ingredient_costs: a dictionary mapping ingredient names to their cost per 100 units
    :type ingredient_costs: dict[str, float]
    :param weekly_budget: the user's weekly budget for purchasing ingredients
    :type weekly_budget: float

    :return: budget efficiency score as a float between 0 and 1 (higher is better)
    :rtype: float
    """

    pantry_stock = pantry.stock
    consumed_stock = get_consumed_stock(meal_plan, pantry_stock)

    total_needed: dict[str, float] = {}
    for day_meals in meal_plan:
        for recipe in day_meals:
            for ingredient_name, quantity_needed in recipe.ingredients.items():
                total_needed[ingredient_name] = total_needed.get(ingredient_name, 0.0) + quantity_needed

    purchase_cost = 0.0
    for ingredient_name, needed in total_needed.items():
        from_pantry = consumed_stock.get(ingredient_name, 0.0)
        to_buy = max(0.0, needed - from_pantry)
        purchase_cost += (to_buy / 100.0) * ingredient_costs.get(ingredient_name, 1.0)

    if purchase_cost == 0.0:
        return 1.0

    efficiency = weekly_budget / purchase_cost
    return min(efficiency, 1.0)


def get_purchase_dependency_score(meal_plan: list[list[Recipe]], pantry: Pantry) -> float:
    """
    Calculates the purchase dependency score for a given meal plan and pantry

    Defined as the proportion of total needed ingredients that are already available in the pantry, weighted by quantity needed. Higher means less dependency on purchasing new ingredients

    :param meal_plan: a list of lists of Recipe objects representing the meal plan
    :type meal_plan: list[list[Recipe]]
    :param pantry: a Pantry object representing the available ingredients
    :type pantry: Pantry

    :return: purchase dependency score as a float between 0 and 1 (higher is better)
    :rtype: float
    """

    pantry_stock = pantry.stock

    total_needed: dict[str, float] = {}
    for day_meals in meal_plan:
        for recipe in day_meals:
            for ingredient_name, quantity_needed in recipe.ingredients.items():
                total_needed[ingredient_name] = total_needed.get(ingredient_name, 0.0) + quantity_needed

    if not total_needed:
        return 1.0

    total_covered = sum(min(pantry_stock.get(name, 0.0), needed) for name, needed in total_needed.items())
    total_required = sum(total_needed.values())

    return total_covered / total_required


def get_variety_score(meal_plan: list[list[Recipe]], num_days: int = 7, meals_per_day: int = 3) -> float:
    """
    Calculates the variety score for a given meal plan

    Defined as the number of unique recipe names used divided by the total number of meal slots (num_days * meals_per_day)

    The result is in [0, 1] where higher means more variety

    :param meal_plan: a list of lists of Recipe objects representing the meal plan
    :type meal_plan: list[list[Recipe]]
    :param num_days: number of days in the plan (default = 7)
    :type num_days: int
    :param meals_per_day: number of meals per day (default = 3)
    :type meals_per_day: int

    :return: variety score as a float between 0 and 1 (higher is better)
    :rtype: float
    """

    total_slots = num_days * meals_per_day
    if total_slots == 0:
        return 0.0

    flat_recipes = [recipe for day_meals in meal_plan for recipe in day_meals]
    unique_count = len(set(recipe.name for recipe in flat_recipes))

    return unique_count / total_slots


def get_optimality_gap(planner_fitness: float, ilp_fitness: float) -> float:
    """
    Calculates the optimality gap between a planner's fitness and the ILP oracle fitness

    Defined as (ILP_fitness - planner_fitness) / ILP_fitness [0, 1], where lower is better

    :param planner_fitness: fitness score achieved by the planner under evaluation
    :type planner_fitness: float
    :param ilp_fitness: fitness score of the ILP oracle (upper bound)
    :type ilp_fitness: float

    :return: optimality gap as a float between 0 and 1 (lower is better)
    :rtype: float
    """

    if ilp_fitness <= 0.0:
        return 0.0

    gap = (ilp_fitness - planner_fitness) / ilp_fitness

    return max(0.0, min(gap, 1.0))
